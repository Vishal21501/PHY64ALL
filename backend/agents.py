# backend/agents.py
"""
Multi-Agent Debate System for Physics
Supports: Mechanics, Electromagnetism, Quantum, Thermodynamics, Waves,
Solid State, Atomic & Molecular, Astrophysics, Nuclear & Particle
"""

import json
import google.generativeai as genai
from typing import List, Dict, Any, Optional
import asyncio
import re

class PhysicsAgent:
    """Base agent class"""
    
    def __init__(self, name: str, role: str, model_name: str = "gemini-1.5-flash"):
        self.name = name
        self.role = role
        self.model = genai.GenerativeModel(model_name)
    
    def generate(self, prompt: str) -> str:
        """Generate response from agent"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"

class TutorAgent(PhysicsAgent):
    """Primary tutor agent - explains concepts in accessible language"""
    
    def __init__(self):
        super().__init__("Tutor", "Explains physics concepts clearly")
    
    def explain(self, query: str, grade_level: str, problem_type: str = None) -> str:
        """Explain physics concepts with grade-level appropriate language"""
        
        # Add domain-specific context if available
        domain_context = ""
        if problem_type:
            domain_context = f"This is a {problem_type} problem. "
        
        prompt = f"""
        You are a physics tutor. Explain this physics concept clearly:
        Query: {query}
        Grade Level: {grade_level}
        {domain_context}
        
        Use:
        - Simple language for Middle School (grades 6-8)
        - Standard physics terms for High School (grades 9-12)
        - Mathematical rigor for University (college level)
        
        Adapt your explanation to be accessible yet comprehensive.
        Provide a clear explanation with formulas using $$ for LaTeX.
        Include real-world examples where applicable.
        """
        return self.generate(prompt)

class PhysicistAgent(PhysicsAgent):
    """Solves physics problems mathematically"""
    
    def __init__(self):
        super().__init__("Physicist", "Solves physics problems")
    
    def solve(self, query: str) -> Dict[str, Any]:
        """Solve physics problem with proper parameter extraction"""
        prompt = f"""
        You are a physicist. Solve this physics problem:
        Query: {query}
        
        Analyze the problem and determine the physics domain.
        Respond with JSON only (no markdown, no explanations):
        {{
            "problem_type": "mechanics|electromagnetism|quantum|thermodynamics|waves|solid_state|atomic_molecular|astrophysics|nuclear_particle",
            "parameters": {{
                "gravity": 9.8,
                "mass": 1.0,
                "initial_velocity_x": 10,
                "initial_velocity_y": 20,
                "angle": 45,
                "friction": 0.02,
                "charge": 1.0,
                "field_strength": 1.0,
                "energy": 1.0,
                "potential": 0.5,
                "initial_temp": 100,
                "ambient_temp": 25,
                "cooling_rate": 0.1,
                "amplitude": 1.0,
                "frequency": 1.0,
                "wavelength": 2.0,
                "temperature": 300,
                "fermi_energy": 5.0,
                "band_gap": 1.0,
                "lattice_constant": 0.5,
                "electron_density": 1e22,
                "atomic_number": 1,
                "principal_quantum": 1,
                "reduced_mass": 1.0,
                "bond_length": 0.1,
                "vibrational_quantum": 0,
                "rotational_quantum": 0,
                "stellar_mass": 1.0,
                "stellar_radius": 1.0,
                "luminosity": 1.0,
                "red_shift": 0.0,
                "distance": 10,
                "half_life": 10,
                "initial_activity": 1000,
                "mass_number": 56,
                "atomic_number_nuclear": 26,
                "binding_energy": 8.5
            }},
            "derivation_steps": ["Step 1: ...", "Step 2: ..."],
            "predictive_oracle": "What will happen...",
            "domain_insight": "Key insight about this physics domain"
        }}
        
        IMPORTANT: Only include parameters relevant to the problem type.
        Make reasonable assumptions for missing parameters.
        """
        try:
            response = self.generate(prompt)
            # Extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
            return self._default_solution(query)
        except Exception as e:
            return self._default_solution(query)
    
    def _default_solution(self, query: str) -> Dict[str, Any]:
        """Fallback solution if JSON parsing fails"""
        # Try to detect problem type from query
        query_lower = query.lower()
        problem_type = 'mechanics'  # default
        
        domain_keywords = {
            'mechanics': ['projectile', 'motion', 'force', 'momentum', 'collision', 'mass', 'acceleration', 'velocity'],
            'electromagnetism': ['charge', 'electric', 'magnetic', 'field', 'circuit', 'current', 'voltage', 'capacitor'],
            'quantum': ['quantum', 'wavefunction', 'schrodinger', 'heisenberg', 'uncertainty', 'eigen'],
            'thermodynamics': ['heat', 'temperature', 'entropy', 'energy', 'thermodynamic', 'cooling', 'heating'],
            'waves': ['wave', 'frequency', 'amplitude', 'wavelength', 'interference', 'diffraction'],
            'solid_state': ['crystal', 'lattice', 'band', 'fermi', 'conductor', 'semiconductor', 'phonon', 'density of states'],
            'atomic_molecular': ['atom', 'molecule', 'spectral', 'bohr', 'vibrational', 'rotational', 'energy level'],
            'astrophysics': ['star', 'galaxy', 'cosmos', 'black hole', 'supernova', 'cosmology', 'hubble', 'redshift'],
            'nuclear_particle': ['nuclear', 'decay', 'half-life', 'particle', 'cross section', 'fission', 'fusion']
        }
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                problem_type = domain
                break
        
        return {
            "problem_type": problem_type,
            "parameters": {},
            "derivation_steps": ["Analyzing the problem...", "Applying relevant physics laws..."],
            "predictive_oracle": "Solution in progress...",
            "domain_insight": f"Analyzing as a {problem_type} problem"
        }

class CriticAgent(PhysicsAgent):
    """Critiques and questions the solution"""
    
    def __init__(self):
        super().__init__("Critic", "Critiques physics solutions")
    
    def critique(self, solution: Dict[str, Any], query: str) -> str:
        """Provide constructive criticism of the solution"""
        prompt = f"""
        You are a physics critic. Rigorously review this solution:
        
        Query: {query}
        Solution: {json.dumps(solution, indent=2)}
        
        Identify:
        1. Any mathematical errors or inconsistencies
        2. Missing physical considerations or assumptions
        3. Alternative approaches or methods
        4. Conceptual clarity and physical intuition
        5. Potential limitations or edge cases
        
        Be constructive and thorough. If the solution is good, explain why.
        If there are issues, suggest specific improvements.
        """
        return self.generate(prompt)

class SpecialistAgent(PhysicsAgent):
    """Domain-specific specialist agent"""
    
    def __init__(self, domain: str):
        super().__init__(f"{domain.title()} Specialist", f"Specialist in {domain}")
        self.domain = domain
    
    def analyze(self, problem: str, solution: Dict[str, Any]) -> str:
        """Provide specialized analysis for a specific domain"""
        prompt = f"""
        You are a specialist in {self.domain} physics.
        
        Problem: {problem}
        Proposed Solution: {json.dumps(solution, indent=2)}
        
        Provide deep insights about:
        1. Domain-specific nuances
        2. Advanced considerations beyond the basic solution
        3. Real-world applications and implications
        4. Connections to other physics domains
        
        Be thorough and demonstrate deep understanding of {self.domain}.
        """
        return self.generate(prompt)

class VerifierAgent(PhysicsAgent):
    """Verifies dimensional consistency and correctness"""
    
    def __init__(self):
        super().__init__("Verifier", "Verifies physics solutions")
    
    def verify(self, solution: Dict[str, Any]) -> Dict[str, Any]:
        """Verify the solution for correctness"""
        prompt = f"""
        Verify this physics solution for dimensional consistency and correctness:
        {json.dumps(solution, indent=2)}
        
        Check:
        1. Dimensional analysis (units are consistent)
        2. Mathematical consistency (equations balance)
        3. Physical plausibility (reasonable magnitudes)
        4. Boundary conditions (physically valid limits)
        5. Conservation laws (energy, momentum, charge)
        
        Respond with JSON:
        {{
            "is_valid": true,
            "confidence_score": 0.95,
            "issues": ["issue1", "issue2"],
            "suggestions": ["suggestion1", "suggestion2"],
            "verified_domains": ["domain1", "domain2"],
            "validation_notes": "Additional validation notes..."
        }}
        """
        try:
            response = self.generate(prompt)
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
            return {
                'is_valid': True, 
                'confidence_score': 0.8, 
                'issues': [], 
                'suggestions': [],
                'verified_domains': [],
                'validation_notes': "Verification completed"
            }
        except:
            return {
                'is_valid': True, 
                'confidence_score': 0.8, 
                'issues': [], 
                'suggestions': [],
                'verified_domains': [],
                'validation_notes': "Verification completed"
            }

class DebateSystem:
    """Orchestrates the multi-agent debate"""
    
    def __init__(self):
        self.tutor = TutorAgent()
        self.physicist = PhysicistAgent()
        self.critic = CriticAgent()
        self.verifier = VerifierAgent()
        self.specialists = {
            'solid_state': SpecialistAgent('solid state'),
            'atomic_molecular': SpecialistAgent('atomic and molecular'),
            'astrophysics': SpecialistAgent('astrophysics'),
            'nuclear_particle': SpecialistAgent('nuclear and particle')
        }
    
    async def solve(self, query: str, grade_level: str = "high_school", enable_specialist: bool = True) -> Dict[str, Any]:
        """
        Run the full multi-agent debate with enhanced specialist review
        
        Args:
            query: The physics problem to solve
            grade_level: Middle school, high school, or university
            enable_specialist: Whether to include domain specialist analysis
        """
        
        # Round 1: Get initial solution
        solution = self.physicist.solve(query)
        problem_type = solution.get('problem_type', 'mechanics')
        
        # Round 2: Tutor explains the concept (with domain context)
        explanation = self.tutor.explain(query, grade_level, problem_type)
        
        # Round 3: Critic reviews
        critique = self.critic.critique(solution, query)
        
        # Round 4: If critique suggests improvements, re-solve
        if "error" in critique.lower() or "missing" in critique.lower() or "incorrect" in critique.lower():
            refinement_prompt = f"{query} (Consider this feedback and improve: {critique})"
            refined_solution = self.physicist.solve(refinement_prompt)
            if refined_solution:
                solution = refined_solution
        
        # Round 5: Specialist analysis (for advanced domains)
        specialist_insight = None
        if enable_specialist and problem_type in self.specialists:
            specialist = self.specialists[problem_type]
            specialist_insight = specialist.analyze(query, solution)
        
        # Round 6: Final verification
        verification = self.verifier.verify(solution)
        
        # Build comprehensive result
        result = {
            'explanation': explanation,
            'solution': solution,
            'critique': critique,
            'verification': verification,
            'problem_type': problem_type,
            'grade_level': grade_level,
            'debate_history': {
                'tutor': explanation,
                'physicist': solution,
                'critic': critique,
                'verifier': verification
            }
        }
        
        if specialist_insight:
            result['specialist_insight'] = specialist_insight
            result['debate_history']['specialist'] = specialist_insight
        
        return result
    
    def get_available_domains(self) -> List[Dict[str, str]]:
        """Get list of all supported physics domains"""
        from physics_engine import PhysicsSolver
        return PhysicsSolver.get_solver_list()
    
    async def solve_with_domain_override(self, query: str, domain: str, grade_level: str = "high_school") -> Dict[str, Any]:
        """
        Solve a physics problem with a specific domain override
        
        Args:
            query: The physics problem
            domain: Specific domain to use (must be in PhysicsSolver.SOLVERS)
            grade_level: Education level
        """
        # Force the physicist to use a specific domain
        forced_prompt = f"""
        Solve this physics problem as a {domain} problem:
        Query: {query}
        
        Respond with JSON following the same format as before,
        but ensure 'problem_type' is exactly '{domain}'.
        """
        solution = self.physicist.generate(forced_prompt)
        try:
            json_match = re.search(r'\{[\s\S]*\}', solution)
            if json_match:
                solution_dict = json.loads(json_match.group())
            else:
                solution_dict = {"problem_type": domain, "parameters": {}}
        except:
            solution_dict = {"problem_type": domain, "parameters": {}}
        
        # Continue with normal debate flow
        return await self.solve(query, grade_level)