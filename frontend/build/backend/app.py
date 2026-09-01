# backend/app.py
"""
Main FastAPI application with Firebase Auth, multi-agent system, and exports
"""

import os
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
import asyncio

from fastapi import FastAPI, HTTPException, Depends, Header, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from pydantic import BaseModel, Field
import firebase_admin
from firebase_admin import credentials, auth, firestore
import google.generativeai as genai
from dotenv import load_dotenv

# Import local modules
from physics_engine import PhysicsSolver
from agents import DebateSystem

# Load environment
load_dotenv()

# ============================================
# Configuration
# ============================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is required")

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
if not PROJECT_ID:
    raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is required")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Firebase Admin
try:
    # For Cloud Run - uses ADC
    firebase_admin.initialize_app()
except:
    # For local development
    cred = credentials.Certificate("service-account.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ============================================
# Models
# ============================================

class PhysicsQuery(BaseModel):
    query: str
    grade_level: str = "high_school"  # middle_school, high_school, university
    enable_sonification: bool = True
    enable_specialist: bool = True
    force_domain: Optional[str] = None  # Override domain detection
    export_format: Optional[str] = None  # pdf, image, video

class SessionResponse(BaseModel):
    session_id: str
    explanation: str
    solution: Dict[str, Any]
    critique: str
    verification: Dict[str, Any]
    numerical_data: List[tuple]
    sonification_frequencies: List[float]
    visualization_config: Dict[str, Any]
    problem_type: str
    grade_level: str
    created_at: str
    specialist_insight: Optional[str] = None

class ExportRequest(BaseModel):
    session_id: str
    format: str = "pdf"  # pdf, image, video, json

# ============================================
# FastAPI App
# ============================================

app = FastAPI(
    title="PHY64ALL - Physics AI Lab",
    version="2.0.0",
    description="Multi-Agent Physics Solver with Accessibility Features"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# Authentication
# ============================================

async def verify_token(authorization: Optional[str] = Header(None)):
    """Verify Firebase Auth token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    try:
        token = authorization.split("Bearer ")[1]
        decoded = auth.verify_id_token(token)
        return decoded
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

# Optional auth (for public endpoints)
async def optional_auth(authorization: Optional[str] = Header(None)):
    """Optional authentication for public endpoints"""
    if not authorization:
        return None
    try:
        token = authorization.split("Bearer ")[1]
        return auth.verify_id_token(token)
    except:
        return None

# ============================================
# API Endpoints
# ============================================

@app.get("/")
async def root():
    return {
        "status": "healthy", 
        "service": "PHY64ALL",
        "version": "2.0.0",
        "domains": PhysicsSolver.get_solver_list()
    }

@app.get("/api/domains")
async def get_domains(user: dict = Depends(optional_auth)):
    """Get all available physics domains"""
    return {
        "domains": PhysicsSolver.get_solver_list(),
        "total": len(PhysicsSolver.SOLVERS)
    }

@app.post("/api/solve")
async def solve_physics(
    query: PhysicsQuery,
    user: dict = Depends(verify_token)
):
    """Solve a physics problem using multi-agent debate"""
    
    try:
        # 1. Initialize debate system
        debate = DebateSystem()
        
        # 2. Run multi-agent debate with optional domain override
        if query.force_domain:
            result = await debate.solve_with_domain_override(
                query.query, 
                query.force_domain,
                query.grade_level
            )
        else:
            result = await debate.solve(
                query.query, 
                query.grade_level,
                query.enable_specialist
            )
        
        # 3. Extract solution and run numerical solver
        solution = result.get('solution', {})
        problem_type = solution.get('problem_type', 'mechanics')
        params = solution.get('parameters', {})
        
        # 4. Run the physics engine
        solver_result = PhysicsSolver.solve(problem_type, params)
        
        # 5. Generate visualization config based on problem type
        viz_config = generate_visualization_config(problem_type, solver_result['numerical_data'])
        
        # 6. Get sonification data
        sonification = solver_result['sonification_frequencies'] if query.enable_sonification else []
        
        # 7. Store in Firestore
        session_id = str(uuid.uuid4())
        session_data = {
            'user_id': user['uid'],
            'query': query.query,
            'grade_level': query.grade_level,
            'problem_type': problem_type,
            'explanation': result['explanation'],
            'solution': result['solution'],
            'critique': result['critique'],
            'verification': result['verification'],
            'numerical_data': solver_result['numerical_data'],
            'column_labels': solver_result.get('column_labels', []),
            'sonification_frequencies': sonification,
            'visualization_config': viz_config,
            'debate_history': result.get('debate_history', {}),
            'specialist_insight': result.get('specialist_insight'),
            'created_at': firestore.SERVER_TIMESTAMP
        }
        
        db.collection('users').document(user['uid']).collection('sessions').document(session_id).set(session_data)
        
        # 8. Prepare response
        response = {
            'session_id': session_id,
            'explanation': result['explanation'],
            'solution': result['solution'],
            'critique': result['critique'],
            'verification': result['verification'],
            'numerical_data': solver_result['numerical_data'],
            'column_labels': solver_result.get('column_labels', []),
            'sonification_frequencies': sonification,
            'visualization_config': viz_config,
            'problem_type': problem_type,
            'grade_level': query.grade_level,
            'debate_history': result.get('debate_history', {})
        }
        
        if result.get('specialist_insight'):
            response['specialist_insight'] = result['specialist_insight']
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sessions")
async def get_sessions(
    user: dict = Depends(verify_token),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get user's session history with pagination"""
    try:
        sessions = db.collection('users').document(user['uid']).collection('sessions')\
            .order_by('created_at', direction=firestore.Query.DESCENDING)\
            .limit(limit).offset(offset).stream()
        
        result = []
        for doc in sessions:
            data = doc.to_dict()
            data['session_id'] = doc.id
            if 'created_at' in data and data['created_at']:
                data['created_at'] = data['created_at'].isoformat()
            # Clean up large fields for listing
            if 'debate_history' in data:
                del data['debate_history']
            if 'solution' in data and isinstance(data['solution'], dict):
                # Keep only essential solution info
                data['solution'] = {
                    'problem_type': data['solution'].get('problem_type'),
                    'parameters': data['solution'].get('parameters', {})
                }
            result.append(data)
        
        return {'sessions': result, 'total': len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str, user: dict = Depends(verify_token)):
    """Get a specific session with full details"""
    try:
        doc = db.collection('users').document(user['uid']).collection('sessions').document(session_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Session not found")
        
        data = doc.to_dict()
        data['session_id'] = doc.id
        if 'created_at' in data and data['created_at']:
            data['created_at'] = data['created_at'].isoformat()
        
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str, user: dict = Depends(verify_token)):
    """Delete a session"""
    try:
        db.collection('users').document(user['uid']).collection('sessions').document(session_id).delete()
        return {"message": "Session deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export")
async def export_session(
    export_request: ExportRequest,
    user: dict = Depends(verify_token)
):
    """Export session in various formats"""
    # Get session data
    doc = db.collection('users').document(user['uid']).collection('sessions').document(export_request.session_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Session not found")
    
    data = doc.to_dict()
    
    # Generate export based on format
    if export_request.format == "json":
        return JSONResponse(content=data)
    
    elif export_request.format == "pdf":
        # Generate PDF (simplified for now)
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
        import io
        
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.drawString(100, 750, f"PHY64ALL - Physics Solution")
        c.drawString(100, 730, f"Query: {data.get('query', '')}")
        c.drawString(100, 710, f"Problem Type: {data.get('problem_type', '')}")
        c.drawString(100, 690, f"Grade Level: {data.get('grade_level', '')}")
        c.drawString(100, 670, f"Generated: {datetime.now().isoformat()}")
        c.showPage()
        c.save()
        buffer.seek(0)
        
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=physics_solution_{export_request.session_id}.pdf"}
        )
    
    elif export_request.format == "image":
        # Generate image using matplotlib
        import matplotlib.pyplot as plt
        import io
        
        numerical_data = data.get('numerical_data', [])
        if numerical_data:
            fig, ax = plt.subplots(figsize=(10, 6))
            x_data = [d[1] for d in numerical_data]
            y_data = [d[2] for d in numerical_data]
            ax.plot(x_data, y_data, 'b-', linewidth=2, label='Trajectory')
            ax.scatter(x_data[0], y_data[0], color='green', s=100, label='Start')
            if len(x_data) > 0:
                ax.scatter(x_data[-1], y_data[-1], color='red', s=100, label='End')
            ax.set_xlabel('X Position')
            ax.set_ylabel('Y Position')
            ax.set_title(f"Physics Trajectory - {data.get('problem_type', '')}")
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            plt.close()
            
            return StreamingResponse(
                buffer,
                media_type="image/png",
                headers={"Content-Disposition": f"attachment; filename=trajectory_{export_request.session_id}.png"}
            )
    
    return {"message": "Export not available for this format"}

# ============================================
# Helper Functions
# ============================================

def generate_visualization_config(problem_type: str, numerical_data: List[tuple]) -> Dict[str, Any]:
    """Generate visualization configuration based on problem type"""
    
    if not numerical_data:
        return {}
    
    # Extract x and y data
    x_data = [d[1] for d in numerical_data]
    y_data = [d[2] for d in numerical_data]
    
    # Different visualization types based on problem
    viz_type = "trajectory"  # default
    
    if problem_type in ["solid_state", "quantum"]:
        viz_type = "energy_spectrum"
    elif problem_type == "astrophysics":
        viz_type = "stellar_evolution"
    elif problem_type == "nuclear_particle":
        viz_type = "decay_curve"
    elif problem_type == "thermodynamics":
        viz_type = "cooling_curve"
    
    return {
        "worldConfig": {
            "gravity": {"x": 0, "y": 1},
            "bounds": {"x": [min(x_data) - 1, max(x_data) + 1], "y": [min(y_data) - 1, max(y_data) + 1]}
        },
        "bodies": [{
            "type": "circle",
            "label": "object",
            "position": {"x": x_data[0] if x_data else 100, "y": y_data[0] if y_data else 400},
            "options": {"radius": 20, "restitution": 0.8}
        }],
        "trajectory": [
            {"x": float(d[1]) * 30 + 100, "y": float(d[2]) * 30 + 300}
            for d in numerical_data
        ],
        "viz_type": viz_type,
        "x_label": "X Position",
        "y_label": "Y Position",
        "title": f"{problem_type.replace('_', ' ').title()} Solution"
    }

# ============================================
# Health Check
# ============================================

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "timestamp": datetime.utcnow().isoformat(),
        "domains_available": len(PhysicsSolver.SOLVERS)
    }

@app.get("/api/stats")
async def get_stats(user: dict = Depends(optional_auth)):
    """Get usage statistics"""
    if not user:
        return {"message": "Authentication required for stats"}
    
    try:
        # Get total sessions
        sessions = db.collection('users').document(user['uid']).collection('sessions').stream()
        total = sum(1 for _ in sessions)
        
        # Get domain distribution
        domain_counts = {}
        for doc in db.collection('users').document(user['uid']).collection('sessions').stream():
            data = doc.to_dict()
            domain = data.get('problem_type', 'unknown')
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        return {
            "total_sessions": total,
            "domain_distribution": domain_counts,
            "user_id": user['uid']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# Main
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)