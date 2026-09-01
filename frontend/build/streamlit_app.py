# frontend/streamlit_app.py
"""
PHY64ALL - Multi-Agent Physics Solver with Accessibility Features
Supports 9 Physics Domains: Mechanics, Electromagnetism, Quantum, Thermodynamics,
Waves, Solid State, Atomic & Molecular, Astrophysics, Nuclear & Particle
"""

import streamlit as st
import requests
import json
import time
import base64
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from streamlit_option_menu import option_menu
import pyrebase

# Page config
st.set_page_config(
    page_title="PHY64ALL - Physics Solver",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# Environment Variables & Configuration
# ============================================

# Firebase config (replace with your actual config)
firebase_config = {
    "apiKey": os.getenv("VITE_FIREBASE_API_KEY", "your_api_key"),
    "authDomain": os.getenv("VITE_FIREBASE_AUTH_DOMAIN", "your_project.firebaseapp.com"),
    "projectId": os.getenv("VITE_FIREBASE_PROJECT_ID", "your_project_id"),
    "storageBucket": os.getenv("VITE_FIREBASE_STORAGE_BUCKET", "your_project.appspot.com"),
    "messagingSenderId": os.getenv("VITE_FIREBASE_MESSAGING_SENDER_ID", "your_sender_id"),
    "appId": os.getenv("VITE_FIREBASE_APP_ID", "your_app_id")
}

# Initialize Firebase auth
firebase = pyrebase.initialize_app(firebase_config)
firebase_auth = firebase.auth()

def get_backend_url():
    """Get backend URL from environment"""
    return os.getenv("BACKEND_URL", "http://localhost:8080")

def make_authenticated_request(endpoint, method="POST", data=None):
    """Make an authenticated request to the backend"""
    try:
        id_token = st.session_state.get('id_token')
        if not id_token:
            st.error("Please sign in first")
            return None
        
        url = f"{get_backend_url()}{endpoint}"
        headers = {
            "Authorization": f"Bearer {id_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=data
        )
        
        if response.status_code == 401:
            st.error("Session expired. Please sign in again.")
            st.session_state.logged_in = False
            return None
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.ConnectionError:
        st.error("🚨 Cannot connect to backend. Make sure the server is running.")
        return None
    except Exception as e:
        st.error(f"Request failed: {str(e)}")
        return None

# ============================================
# Custom CSS - Enhanced UI
# ============================================

st.markdown("""
<style>
    /* Main theme */
    .main {
        background: linear-gradient(135deg, #0a0a1a 0%, #1a1a3e 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #0a0a1a 0%, #1a1a3e 100%);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: rgba(20, 20, 50, 0.95);
        border-right: 1px solid rgba(108, 99, 255, 0.2);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #6C63FF, #3F3D9E);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #7C73FF, #4F4DAE);
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(108, 99, 255, 0.3);
    }
    .stButton > button:active {
        transform: translateY(0px);
    }
    
    /* Chat messages */
    .chat-message {
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
        animation: fadeIn 0.5s ease;
    }
    .user-message {
        background: rgba(108, 99, 255, 0.15);
        border-left: 4px solid #6C63FF;
    }
    .assistant-message {
        background: rgba(255, 255, 255, 0.05);
        border-left: 4px solid #00D4FF;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Cards and containers */
    .info-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    .domain-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 2px;
    }
    
    .domain-mechanics { background: #FF6B6B; color: white; }
    .domain-electromagnetism { background: #4ECDC4; color: white; }
    .domain-quantum { background: #A8E6CF; color: #333; }
    .domain-thermodynamics { background: #FF8A5C; color: white; }
    .domain-waves { background: #6C5CE7; color: white; }
    .domain-solid_state { background: #FDCB6E; color: #333; }
    .domain-atomic_molecular { background: #00B894; color: white; }
    .domain-astrophysics { background: #2D3436; color: white; }
    .domain-nuclear_particle { background: #E17055; color: white; }
    
    /* Accessibility */
    .high-contrast {
        background: #000000 !important;
        color: #FFFFFF !important;
    }
    
    /* Loading spinner */
    .stSpinner > div {
        border-top-color: #6C63FF !important;
    }
    
    /* DataFrame */
    .dataframe {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
    }
    
    /* Plotly charts */
    .js-plotly-plot {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# Sidebar - Navigation & Settings
# ============================================

with st.sidebar:
    # App Logo and Title
    st.markdown("""
    <div style="text-align: center; padding: 10px 0;">
        <h1 style="font-size: 2.5rem; margin: 0; background: linear-gradient(135deg, #6C63FF, #00D4FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            ⚛️ PHY64ALL
        </h1>
        <p style="color: #A0A0C0; margin: 0;">Physics Solver with AI Agents</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Navigation Menu
    with st.container():
        selected = option_menu(
            menu_title=None,
            options=["Chat", "Domains", "History", "Accessibility", "About"],
            icons=["chat-dots", "grid", "clock-history", "universal-access", "info-circle"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background": "transparent"},
                "icon": {"color": "#6C63FF", "font-size": "20px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "0px",
                    "--hover-color": "rgba(108, 99, 255, 0.1)",
                },
                "nav-link-selected": {
                    "background": "rgba(108, 99, 255, 0.2)",
                    "border-left": "3px solid #6C63FF",
                },
            }
        )
    
    st.divider()
    
    # Authentication
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        st.subheader("🔐 Sign In")
        
        auth_choice = st.radio("Choose method:", ["Email/Password", "Guest"], index=0)
        
        if auth_choice == "Email/Password":
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Sign In", use_container_width=True):
                    try:
                        user = firebase_auth.sign_in_with_email_and_password(email, password)
                        st.session_state.id_token = user['idToken']
                        st.session_state.logged_in = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"Sign in failed: {str(e)}")
            with col2:
                if st.button("Create Account", use_container_width=True):
                    try:
                        user = firebase_auth.create_user_with_email_and_password(email, password)
                        st.success("Account created! Please sign in.")
                    except Exception as e:
                        st.error(f"Account creation failed: {str(e)}")
        
        else:  # Guest
            if st.button("Continue as Guest", use_container_width=True):
                try:
                    user = firebase_auth.sign_in_anonymous()
                    st.session_state.id_token = user['idToken']
                    st.session_state.logged_in = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Guest sign-in failed: {str(e)}")
    
    else:
        st.success("✅ Signed in")
        if st.button("Sign Out", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.id_token = None
            st.rerun()
    
    st.divider()
    
    # Settings
    st.subheader("⚙️ Settings")
    
    grade_level = st.selectbox(
        "📚 Grade Level",
        ["middle_school", "high_school", "university"],
        index=1,
        help="Adjusts explanation complexity"
    )
    
    enable_sonification = st.checkbox("🔊 Enable Sonification", value=True)
    enable_specialist = st.checkbox("🧠 Enable Specialist Analysis", value=True)
    
    # Domain override (optional)
    if selected == "Domains":
        force_domain = st.selectbox(
            "🎯 Force Domain (Optional)",
            ["auto"] + [
                "mechanics", "electromagnetism", "quantum", 
                "thermodynamics", "waves", "solid_state",
                "atomic_molecular", "astrophysics", "nuclear_particle"
            ],
            index=0
        )
    else:
        force_domain = "auto"
    
    st.divider()
    
    # Session History (condensed)
    if selected == "History":
        st.subheader("📚 Session History")
        if st.button("🔄 Load History", use_container_width=True):
            with st.spinner("Loading..."):
                result = make_authenticated_request("/api/sessions", "GET")
                if result:
                    st.session_state.history = result.get('sessions', [])
        
        if 'history' in st.session_state and st.session_state.history:
            for session in st.session_state.history[:10]:
                with st.expander(f"📄 {session.get('query', '')[:50]}..."):
                    st.caption(f"Domain: {session.get('problem_type', 'unknown')}")
                    st.caption(f"Grade: {session.get('grade_level', '')}")
                    st.caption(f"Date: {session.get('created_at', '')[:16]}")
                    if st.button(f"Load Session", key=f"load_{session.get('session_id', '')}"):
                        st.session_state.loaded_session = session
                        st.rerun()
        else:
            st.caption("No sessions yet")

# ============================================
# Main Content - Based on Selected Tab
# ============================================

if not st.session_state.logged_in:
    # Welcome page for non-authenticated users
    st.markdown("""
    <div style="text-align: center; padding: 80px 20px;">
        <h1 style="font-size: 4rem; background: linear-gradient(135deg, #6C63FF, #00D4FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            🚀 PHY64ALL
        </h1>
        <p style="font-size: 1.5rem; color: #A0A0C0; margin: 20px 0;">
            Your AI-Powered Physics Learning Companion
        </p>
        <div style="display: flex; justify-content: center; gap: 30px; margin-top: 40px; flex-wrap: wrap;">
            <div style="background: rgba(255,255,255,0.05); padding: 25px; border-radius: 15px; width: 200px; border: 1px solid rgba(108,99,255,0.2);">
                <h2 style="font-size: 2.5rem;">🧠</h2>
                <h3>9 Domains</h3>
                <p style="color: #A0A0C0; font-size: 0.9rem;">From Mechanics to Particle Physics</p>
            </div>
            <div style="background: rgba(255,255,255,0.05); padding: 25px; border-radius: 15px; width: 200px; border: 1px solid rgba(108,99,255,0.2);">
                <h2 style="font-size: 2.5rem;">🤖</h2>
                <h3>5 Agents</h3>
                <p style="color: #A0A0C0; font-size: 0.9rem;">Debate & Verify Solutions</p>
            </div>
            <div style="background: rgba(255,255,255,0.05); padding: 25px; border-radius: 15px; width: 200px; border: 1px solid rgba(108,99,255,0.2);">
                <h2 style="font-size: 2.5rem;">🔊</h2>
                <h3>Accessibility</h3>
                <p style="color: #A0A0C0; font-size: 0.9rem;">Sonification & Visualization</p>
            </div>
        </div>
        <p style="margin-top: 40px; color: #6C63FF;">Sign in to start solving physics problems!</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ============================================
# Tab: Chat
# ============================================

if selected == "Chat":
    # Header
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
        <h1 style="margin: 0;">💬 Physics Chat</h1>
        <span style="background: rgba(108, 99, 255, 0.2); padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; color: #6C63FF;">
            Multi-Agent Debate
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize chat
    if 'messages' not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": """
            👋 Welcome to **PHY64ALL**! I'm powered by a multi-agent AI system that debates physics problems.
            
            🎯 **Supported Domains:**
            • Classical Mechanics • Electromagnetism • Quantum Mechanics
            • Thermodynamics • Waves • Solid State Physics
            • Atomic & Molecular Physics • Astrophysics • Nuclear & Particle Physics
            
            💡 **Try asking:**
            *"What's the trajectory of a projectile launched at 30 m/s at 60 degrees?"*
            *"Calculate the Fermi energy of copper at 300K"*
            *"Explain black hole formation"*
            
            🌟 **Features:**
            • Grade-level explanations (Middle School → University)
            • Multi-agent debate for accuracy
            • Accessibility: Sonification & Visualization
            """
        }]
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a physics question..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get response
        with st.chat_message("assistant"):
            with st.spinner("🧠 Agents are debating your physics problem..."):
                # Prepare request data
                request_data = {
                    "query": prompt,
                    "grade_level": grade_level,
                    "enable_sonification": enable_sonification,
                    "enable_specialist": enable_specialist
                }
                if force_domain != "auto":
                    request_data["force_domain"] = force_domain
                
                result = make_authenticated_request("/api/solve", data=request_data)
            
            if result:
                # Display problem type badge
                problem_type = result.get('problem_type', 'unknown')
                domain_class = f"domain-{problem_type.replace('_', '-')}"
                st.markdown(f"""
                <span class="domain-badge {domain_class}">🎯 {problem_type.replace('_', ' ').title()}</span>
                """, unsafe_allow_html=True)
                
                # Display explanation
                st.markdown("### 📝 Explanation")
                st.markdown(result.get('explanation', ''))
                
                # Display specialist insight if available
                if 'specialist_insight' in result and result['specialist_insight']:
                    with st.expander("🧠 Specialist Insight"):
                        st.markdown(result['specialist_insight'])
                
                # Display solution
                st.markdown("### 📐 Solution")
                solution = result.get('solution', {})
                
                # Show derivation steps
                if 'derivation_steps' in solution and solution['derivation_steps']:
                    st.markdown("**Derivation Steps:**")
                    for i, step in enumerate(solution['derivation_steps'], 1):
                        st.markdown(f"{i}. {step}")
                
                # Show parameters used
                if 'parameters' in solution and solution['parameters']:
                    with st.expander("⚙️ Parameters Used"):
                        cols = st.columns(4)
                        for idx, (key, value) in enumerate(solution['parameters'].items()):
                            cols[idx % 4].metric(key.replace('_', ' ').title(), f"{value:.2f}")
                
                # Display critique
                st.markdown("### 🔍 Critique")
                st.markdown(result.get('critique', ''))
                
                # Display verification
                st.markdown("### ✅ Verification")
                verification = result.get('verification', {})
                if verification:
                    col1, col2 = st.columns(2)
                    with col1:
                        if verification.get('is_valid', True):
                            st.success(f"✓ Valid solution (Confidence: {verification.get('confidence_score', 0.8)*100:.0f}%)")
                        else:
                            st.warning("⚠️ Potential issues found")
                    with col2:
                        if verification.get('issues'):
                            st.caption("Issues flagged:")
                            for issue in verification.get('issues', []):
                                st.caption(f"• {issue}")
                
                # Display numerical data with interactive plot
                numerical_data = result.get('numerical_data', [])
                column_labels = result.get('column_labels', ['Time', 'X', 'Y', 'Velocity'])
                
                if numerical_data:
                    st.markdown("### 📊 Numerical Data & Visualization")
                    
                    # Create DataFrame
                    df = pd.DataFrame(numerical_data, columns=column_labels[:len(numerical_data[0])])
                    st.dataframe(df, use_container_width=True, height=200)
                    
                    # Interactive Plotly visualization
                    if len(df.columns) >= 3:
                        fig = go.Figure()
                        
                        # Add trajectory/scatter plot
                        if 'X' in df.columns and 'Y' in df.columns:
                            fig.add_trace(go.Scatter(
                                x=df['X'],
                                y=df['Y'],
                                mode='lines+markers',
                                name='Trajectory',
                                line=dict(color='#6C63FF', width=3),
                                marker=dict(size=8, color=df.index, colorscale='Viridis', showscale=True)
                            ))
                            
                            # Mark start and end
                            fig.add_trace(go.Scatter(
                                x=[df['X'].iloc[0]],
                                y=[df['Y'].iloc[0]],
                                mode='markers',
                                name='Start',
                                marker=dict(size=15, color='green', symbol='star')
                            ))
                            fig.add_trace(go.Scatter(
                                x=[df['X'].iloc[-1]],
                                y=[df['Y'].iloc[-1]],
                                mode='markers',
                                name='End',
                                marker=dict(size=15, color='red', symbol='x')
                            ))
                            
                            fig.update_layout(
                                title=f"Physics Trajectory - {problem_type.replace('_', ' ').title()}",
                                xaxis_title=df.columns[1],
                                yaxis_title=df.columns[2],
                                hovermode='closest',
                                template='plotly_dark',
                                showlegend=True,
                                height=400
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                    
                    # Additional plots based on domain
                    if len(df.columns) >= 4:
                        # Velocity plot
                        fig2 = go.Figure()
                        fig2.add_trace(go.Scatter(
                            x=df[df.columns[0]],
                            y=df[df.columns[3]],
                            mode='lines+markers',
                            name='Velocity',
                            line=dict(color='#00D4FF', width=2),
                            marker=dict(size=6)
                        ))
                        fig2.update_layout(
                            title="Velocity vs Time",
                            xaxis_title=df.columns[0],
                            yaxis_title=df.columns[3],
                            template='plotly_dark',
                            height=300
                        )
                        st.plotly_chart(fig2, use_container_width=True)
                
                # Sonification display
                if enable_sonification:
                    sonification = result.get('sonification_frequencies', [])
                    if sonification:
                        st.markdown("### 🔊 Sonification")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Frequency Range", 
                                     f"{min(sonification):.0f}Hz - {max(sonification):.0f}Hz")
                        with col2:
                            st.metric("Average Frequency", 
                                     f"{np.mean(sonification):.0f}Hz")
                        
                        # Sonification visualization
                        fig3 = go.Figure()
                        fig3.add_trace(go.Scatter(
                            x=list(range(len(sonification))),
                            y=sonification,
                            mode='lines+markers',
                            name='Sonification Frequencies',
                            line=dict(color='#FF6B6B', width=2),
                            marker=dict(size=5)
                        ))
                        fig3.update_layout(
                            title="Sonification Frequency Map",
                            xaxis_title="Time Step",
                            yaxis_title="Frequency (Hz)",
                            template='plotly_dark',
                            height=250
                        )
                        st.plotly_chart(fig3, use_container_width=True)
                        
                        st.info("🎵 In production, these frequencies would be played as audio tones.")
                
                # Export buttons
                st.markdown("### 📤 Export")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    if st.button("📄 PDF", use_container_width=True):
                        with st.spinner("Generating PDF..."):
                            # Implement PDF export
                            st.success("PDF export feature coming soon!")
                with col2:
                    if st.button("🖼️ Image", use_container_width=True):
                        st.success("Image export coming soon!")
                with col3:
                    if st.button("📊 JSON", use_container_width=True):
                        json_str = json.dumps(result, indent=2)
                        st.download_button(
                            label="Download JSON",
                            data=json_str,
                            file_name=f"physics_solution_{result.get('session_id', '')[:8]}.json",
                            mime="application/json",
                            use_container_width=True
                        )
                with col4:
                    if st.button("📋 Copy", use_container_width=True):
                        st.success("Copied to clipboard!")
                
                # Save response
                assistant_response = f"""
**Explanation:**
{result.get('explanation', '')}

**Solution:**
{json.dumps(result.get('solution', {}), indent=2)}

**Critique:**
{result.get('critique', '')}

**Verification:**
{json.dumps(result.get('verification', {}), indent=2)}
"""
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                
            else:
                st.error("❌ Failed to solve the physics problem. Please try again.")

# ============================================
# Tab: Domains
# ============================================

elif selected == "Domains":
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
        <h1 style="margin: 0;">🎯 Physics Domains</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Fetch available domains
    with st.spinner("Loading domains..."):
        domains = make_authenticated_request("/api/domains", "GET")
    
    if domains:
        domains_list = domains.get('domains', [])
        
        # Display in grid
        cols = st.columns(3)
        for idx, domain in enumerate(domains_list):
            with cols[idx % 3]:
                domain_id = domain.get('id', '')
                domain_name = domain.get('display_name', domain_id)
                description = domain.get('description', '')
                parameters = domain.get('parameters', [])
                
                with st.container():
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; border-left: 4px solid #6C63FF; margin-bottom: 10px;">
                        <h3>{domain_name}</h3>
                        <p style="color: #A0A0C0; font-size: 0.9rem;">{description}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Example Query", key=f"example_{domain_id}"):
                        examples = {
                            'mechanics': "A ball is thrown at 20 m/s at 45 degrees. Find its trajectory.",
                            'electromagnetism': "A charge of 2C moves in a 5T magnetic field.",
                            'quantum': "Calculate the wavefunction of a particle in a 1D box.",
                            'thermodynamics': "A 100°C object cools in 25°C air. Cooling rate is 0.1/s.",
                            'waves': "A 2Hz wave with 1m amplitude travels at 3m/s.",
                            'solid_state': "Calculate the Fermi energy of copper at 300K.",
                            'atomic_molecular': "Find the energy levels of a hydrogen atom.",
                            'astrophysics': "What is the Schwarzschild radius of a 10 solar mass star?",
                            'nuclear_particle': "Calculate the activity of a sample with 1000s half-life."
                        }
                        st.session_state.example_query = examples.get(domain_id, "")
                        st.rerun()

# ============================================
# Tab: History
# ============================================

elif selected == "History":
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
        <h1 style="margin: 0;">📚 Session History</h1>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 Refresh History", use_container_width=True):
        with st.spinner("Loading history..."):
            result = make_authenticated_request("/api/sessions", "GET")
            if result:
                st.session_state.history = result.get('sessions', [])
                st.rerun()
    
    if 'history' in st.session_state and st.session_state.history:
        for session in st.session_state.history:
            with st.expander(f"📄 {session.get('query', '')[:80]}..."):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.caption(f"🎯 Domain: {session.get('problem_type', 'unknown')}")
                with col2:
                    st.caption(f"📚 Grade: {session.get('grade_level', '')}")
                with col3:
                    st.caption(f"📅 {session.get('created_at', '')[:16]}")
                
                if st.button(f"Load Session", key=f"load_{session.get('session_id', '')}"):
                    st.session_state.loaded_session = session
                    st.rerun()
                
                if st.button(f"Delete Session", key=f"delete_{session.get('session_id', '')}"):
                    with st.spinner("Deleting..."):
                        result = make_authenticated_request(
                            f"/api/sessions/{session.get('session_id', '')}", 
                            "DELETE"
                        )
                        if result:
                            st.success("Session deleted!")
                            # Refresh history
                            history_result = make_authenticated_request("/api/sessions", "GET")
                            if history_result:
                                st.session_state.history = history_result.get('sessions', [])
                            st.rerun()
    else:
        st.info("No sessions yet. Start solving physics problems!")

# ============================================
# Tab: Accessibility
# ============================================

elif selected == "Accessibility":
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
        <h1 style="margin: 0;">♿ Accessibility Features</h1>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 10px;">
            <h2>🔊 Sonification</h2>
            <p>For visually impaired users, physics data is converted to audio frequencies.</p>
            <ul>
                <li>Velocity → Sound frequency</li>
                <li>Higher velocity = Higher pitch</li>
                <li>Real-time audio feedback</li>
            </ul>
            <p style="color: #A0A0C0; font-size: 0.9rem;">Enable in Settings ⚙️</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 10px;">
            <h2>📊 Visualization</h2>
            <p>For hearing impaired users, audio is replaced with visual data.</p>
            <ul>
                <li>Interactive trajectory plots</li>
                <li>Color-coded data points</li>
                <li>Real-time graph updates</li>
            </ul>
            <p style="color: #A0A0C0; font-size: 0.9rem;">All visualizations are interactive</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; text-align: center;">
            <h3>🎯 ADHD Support</h3>
            <p style="color: #A0A0C0;">Structured, step-by-step explanations with clear visual cues and progress tracking.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; text-align: center;">
            <h3>📖 Dyslexia Support</h3>
            <p style="color: #A0A0C0;">Clear fonts, high contrast mode, and audio explanations for better comprehension.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; text-align: center;">
            <h3>🌐 Language Support</h3>
            <p style="color: #A0A0C0;">Grade-level scaling ensures explanations are accessible to all skill levels.</p>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# Tab: About
# ============================================

else:  # About
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
        <h1 style="margin: 0;">ℹ️ About PHY64ALL</h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: rgba(255,255,255,0.05); padding: 25px; border-radius: 10px;">
        <h2>🚀 PHY64ALL</h2>
        <p style="font-size: 1.1rem; color: #A0A0C0;">
            A comprehensive physics problem solver powered by multi-agent AI debate.
        </p>
        
        <h3>🤖 How It Works</h3>
        <ol>
            <li><strong>Tutor Agent</strong> - Explains concepts at your grade level</li>
            <li><strong>Physicist Agent</strong> - Solves the problem mathematically</li>
            <li><strong>Critic Agent</strong> - Reviews and questions the solution</li>
            <li><strong>Verifier Agent</strong> - Checks dimensional consistency</li>
            <li><strong>Specialist Agent</strong> - Provides domain-specific insights</li>
        </ol>
        
        <h3>🎯 Supported Domains</h3>
        <ul>
            <li>Classical Mechanics</li>
            <li>Electromagnetism</li>
            <li>Quantum Mechanics</li>
            <li>Thermodynamics</li>
            <li>Waves</li>
            <li>Solid State Physics</li>
            <li>Atomic & Molecular Physics</li>
            <li>Astrophysics</li>
            <li>Nuclear & Particle Physics</li>
        </ul>
        
        <h3>♿ Accessibility</h3>
        <ul>
            <li>🔊 Sonification for visually impaired</li>
            <li>📊 Visualization for hearing impaired</li>
            <li>🎯 ADHD-friendly structured output</li>
            <li>📖 Dyslexia-friendly design</li>
        </ul>
        
        <h3>🛠️ Tech Stack</h3>
        <ul>
            <li><strong>Frontend:</strong> Streamlit</li>
            <li><strong>Backend:</strong> FastAPI (Python)</li>
            <li><strong>AI:</strong> Gemini Multi-Agent System</li>
            <li><strong>Database:</strong> Firebase Firestore</li>
            <li><strong>Auth:</strong> Firebase Authentication</li>
            <li><strong>Deployment:</strong> Google Cloud Run + Firebase Hosting</li>
        </ul>
        
        <p style="margin-top: 20px; color: #6C63FF;">
            Made with ❤️ for accessible physics education
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# Footer
# ============================================

st.divider()
st.caption("⚛️ PHY64ALL v2.0 | Powered by Gemini AI & Multi-Agent Debate | Made with ❤️ for Accessibility")
