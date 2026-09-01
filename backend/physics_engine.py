# backend/physics_engine.py
"""
Fixed physics solvers - NO AI-generated code execution
All numerical computation is done by these human-written functions
"""

import numpy as np
import math
from typing import Dict, List, Tuple, Any, Optional
from scipy import constants
from scipy.special import hermite, factorial
from scipy.integrate import odeint
import sympy as sp

class PhysicsSolver:
    """Fixed solvers for different physics domains"""
    
    # ============================================================
    # CLASSICAL MECHANICS
    # ============================================================
    @staticmethod
    def mechanics(params: Dict[str, float]) -> List[Tuple[float, ...]]:
        """Solve mechanics problems (projectile, freefall, etc.)"""
        g = np.clip(params.get('gravity', 9.8), 0.1, 30)
        mass = np.clip(params.get('mass', 1.0), 0.01, 1000)
        vx = np.clip(params.get('initial_velocity_x', 10), -50, 50)
        vy = np.clip(params.get('initial_velocity_y', 20), -50, 50)
        angle = np.clip(params.get('angle', 45), 0, 90)
        friction = np.clip(params.get('friction', 0.02), 0, 1)
        
        dt = 0.08
        steps = 24
        
        rad = math.radians(angle)
        vx_initial = vx * math.cos(rad)
        vy_initial = vy * math.sin(rad)
        
        results = []
        x, y = 0.0, 0.0
        vx_cur, vy_cur = vx_initial, vy_initial
        
        for i in range(steps):
            t = i * dt
            vy_cur -= g * dt
            vx_cur *= (1 - friction * dt)
            vy_cur *= (1 - friction * dt)
            x += vx_cur * dt
            y += vy_cur * dt
            speed = math.hypot(vx_cur, vy_cur)
            results.append((round(t, 3), round(x, 3), round(max(y, 0), 3), round(speed, 3)))
            if y < 0:
                break
        
        return results
    
    # ============================================================
    # ELECTROMAGNETISM
    # ============================================================
    @staticmethod
    def electromagnetism(params: Dict[str, float]) -> List[Tuple[float, ...]]:
        """Solve electromagnetism problems"""
        charge = np.clip(params.get('charge', 1.0), -10, 10)
        field = np.clip(params.get('field_strength', 1.0), 0.1, 100)
        mass = np.clip(params.get('mass', 1.0), 0.01, 100)
        
        dt = 0.08
        steps = 24
        results = []
        x, y = 0.0, 0.0
        vx, vy = 5.0, 0.0
        acceleration = (charge * field) / mass
        
        for i in range(steps):
            t = i * dt
            vy += acceleration * dt
            x += vx * dt
            y += vy * dt
            speed = math.hypot(vx, vy)
            results.append((round(t, 3), round(x, 3), round(y, 3), round(speed, 3)))
        
        return results
    
    # ============================================================
    # QUANTUM MECHANICS
    # ============================================================
    @staticmethod
    def quantum(params: Dict[str, float]) -> List[Tuple[float, ...]]:
        """Solve quantum mechanics problems (simplified)"""
        energy = np.clip(params.get('energy', 1.0), 0.1, 10)
        potential = np.clip(params.get('potential', 0.5), 0, 10)
        
        dt = 0.1
        steps = 24
        results = []
        x = 0.0
        probability = 1.0 if energy > potential else 0.0
        
        for i in range(steps):
            t = i * dt
            wave = math.sin(energy * t) * math.exp(-potential * x)
            velocity = abs(wave * energy)
            results.append((round(t, 3), round(x, 3), round(probability * 10, 3), round(velocity, 3)))
            x += 0.1
        
        return results
    
    # ============================================================
    # THERMODYNAMICS
    # ============================================================
    @staticmethod
    def thermodynamics(params: Dict[str, float]) -> List[Tuple[float, ...]]:
        """Solve thermodynamics/heat transfer problems"""
        initial_temp = np.clip(params.get('initial_temp', 100), -273, 1000)
        ambient_temp = np.clip(params.get('ambient_temp', 25), -273, 1000)
        cooling_rate = np.clip(params.get('cooling_rate', 0.1), 0.01, 1)
        
        dt = 0.5
        steps = 24
        results = []
        temp = initial_temp
        
        for i in range(steps):
            t = i * dt
            temp = ambient_temp + (temp - ambient_temp) * math.exp(-cooling_rate * t)
            velocity = abs(temp - ambient_temp)
            results.append((round(t, 3), round(temp, 3), 0.0, round(velocity, 3)))
        
        return results
    
    # ============================================================
    # WAVES
    # ============================================================
    @staticmethod
    def waves(params: Dict[str, float]) -> List[Tuple[float, ...]]:
        """Solve wave mechanics problems"""
        amplitude = np.clip(params.get('amplitude', 1.0), 0.1, 10)
        frequency = np.clip(params.get('frequency', 1.0), 0.1, 10)
        wavelength = np.clip(params.get('wavelength', 2.0), 0.1, 10)
        
        dt = 0.1
        steps = 24
        results = []
        speed = frequency * wavelength
        x = 0.0
        
        for i in range(steps):
            t = i * dt
            y = amplitude * math.sin(2 * math.pi * (t / wavelength - x / speed))
            velocity = amplitude * 2 * math.pi * frequency * math.cos(2 * math.pi * (t / wavelength - x / speed))
            results.append((round(t, 3), round(x, 3), round(y, 3), round(abs(velocity), 3)))
            x += 0.5
        
        return results
    
    # ============================================================
    # SOLID STATE PHYSICS
    # ============================================================
    @staticmethod
    def solid_state(params: Dict[str, float]) -> List[Tuple[float, ...]]:
        """
        Solve solid state physics problems:
        - Band structure (E-k diagram)
        - Density of states
        - Phonon dispersion
        - Fermi energy at different temperatures
        """
        # Parameters
        temperature = np.clip(params.get('temperature', 300), 0, 1000)  # Kelvin
        fermi_energy = np.clip(params.get('fermi_energy', 5.0), 0.1, 20)  # eV
        band_gap = np.clip(params.get('band_gap', 1.0), 0, 10)  # eV
        lattice_constant = np.clip(params.get('lattice_constant', 0.5), 0.1, 2)  # nm
        electron_density = np.clip(params.get('electron_density', 1e22), 1e20, 1e24)  # m^-3
        
        dt = 0.05
        steps = 30
        results = []
        
        # Constants
        k_B = 8.617333262145e-5  # eV/K
        h_bar = 6.582119569e-16  # eV·s
        
        # Calculate Fermi-Dirac distribution at different energies
        for i in range(steps):
            t = i * dt
            energy = t * 0.5  # Energy in eV
            
            # Fermi-Dirac distribution
            if temperature > 0:
                fd = 1 / (1 + math.exp((energy - fermi_energy) / (k_B * temperature)))
            else:
                fd = 1.0 if energy < fermi_energy else 0.0
            
            # Simple parabolic dispersion
            k = math.sqrt(2 * (energy) * 9.109e-31 / (h_bar**2)) * 1e-9
            
            # Density of states (simplified 3D)
            dos = 0.5 * math.sqrt(energy) if energy > 0 else 0
            
            # Fermi velocity
            v_f = math.sqrt(2 * energy / 9.109e-31) if energy > 0 else 0
            
            results.append((
                round(t, 3),                    # time/index
                round(energy, 3),               # energy (eV)
                round(fd, 4),                   # Fermi-Dirac occupancy
                round(dos, 3),                  # Density of states (arb units)
                round(v_f * 1e-6, 3)            # Fermi velocity (km/s)
            ))
        
        return results
    
    # ============================================================
    # ATOMIC AND MOLECULAR PHYSICS
    # ============================================================
    @staticmethod
    def atomic_molecular(params: Dict[str, float]) -> List[Tuple[float, ...]]:
        """
        Solve atomic and molecular physics problems:
        - Energy levels (Bohr model)
        - Spectral lines
        - Molecular vibrations (harmonic oscillator)
        - Rotational spectra
        """
        # Parameters
        atomic_number = int(np.clip(params.get('atomic_number', 1), 1, 92))
        principal_quantum = int(np.clip(params.get('principal_quantum', 1), 1, 10))
        reduced_mass = np.clip(params.get('reduced_mass', 1.0), 0.1, 100)  # in atomic mass units
        bond_length = np.clip(params.get('bond_length', 0.1), 0.01, 1)  # nm
        vibrational_quantum = int(np.clip(params.get('vibrational_quantum', 0), 0, 10))
        rotational_quantum = int(np.clip(params.get('rotational_quantum', 0), 0, 10))
        
        dt = 0.1
        steps = 25
        results = []
        
        # Constants
        Rydberg = 13.6  # eV
        h_bar = 1.054571817e-34  # J·s
        
        for i in range(steps):
            t = i * dt
            
            # Bohr energy levels (hydrogenic)
            if atomic_number > 0:
                energy_level = -Rydberg * (atomic_number**2) / (principal_quantum**2)
            else:
                energy_level = -Rydberg / (principal_quantum**2)
            
            # Vibrational energy (harmonic oscillator)
            omega = 0.5  # vibrational frequency (arbitrary units)
            vib_energy = (vibrational_quantum + 0.5) * omega
            
            # Rotational energy (rigid rotor)
            rot_energy = rotational_quantum * (rotational_quantum + 1) * 0.1
            
            # Total energy
            total_energy = energy_level + vib_energy + rot_energy
            
            # Spectral line wavelength (simplified)
            wavelength = 1240 / abs(energy_level) if abs(energy_level) > 0 else 0  # nm
            
            results.append((
                round(t, 3),                    # time/index
                round(energy_level, 3),         # Electronic energy (eV)
                round(vib_energy, 3),           # Vibrational energy (eV)
                round(rot_energy, 3),           # Rotational energy (eV)
                round(total_energy, 3),         # Total energy (eV)
                round(wavelength, 1)            # Wavelength (nm)
            ))
        
        return results
    
    # ============================================================
    # ASTROPHYSICS
    # ============================================================
    @staticmethod
    def astrophysics(params: Dict[str, float]) -> List[Tuple[float, ...]]:
        """
        Solve astrophysics problems:
        - Stellar evolution (main sequence)
        - Gravitational dynamics
        - Black hole properties
        - Cosmic expansion
        """
        # Parameters
        mass_star = np.clip(params.get('stellar_mass', 1.0), 0.1, 100)  # Solar masses
        radius_star = np.clip(params.get('stellar_radius', 1.0), 0.1, 100)  # Solar radii
        luminosity = np.clip(params.get('luminosity', 1.0), 0.01, 1e6)  # Solar luminosities
        temperature = np.clip(params.get('temperature', 5780), 1000, 50000)  # Kelvin
        red_shift = np.clip(params.get('red_shift', 0.0), 0, 10)
        distance = np.clip(params.get('distance', 10), 1, 1000)  # parsecs
        
        dt = 1.0
        steps = 25
        results = []
        
        # Constants
        G = 6.67430e-11  # m^3 kg^-1 s^-2
        c = 299792458  # m/s
        M_sun = 1.98847e30  # kg
        R_sun = 6.957e8  # m
        
        for i in range(steps):
            t = i * dt
            
            # Main sequence lifetime (approximate)
            lifetime = 1e10 * (mass_star**-2.5)  # years
            age_fraction = min(t / lifetime, 1.0)
            
            # Schwarzschild radius (for black hole)
            mass_kg = mass_star * M_sun
            r_s = 2 * G * mass_kg / (c**2)
            r_s_solar_units = r_s / R_sun
            
            # Luminosity-temperature relation (Stefan-Boltzmann)
            L_actual = 4 * math.pi * (radius_star * R_sun)**2 * 5.67e-8 * temperature**4
            L_solar_units = L_actual / (3.828e26)
            
            # Hubble expansion (simplified)
            H0 = 70  # km/s/Mpc
            v_recession = H0 * distance / 1000  # km/s
            
            # Doppler shift
            if red_shift > 0:
                doppler_factor = math.sqrt((1 + red_shift) / (1 - red_shift))
            else:
                doppler_factor = 1.0
            
            results.append((
                round(t, 1),                    # time (million years)
                round(lifetime / 1e6, 1),       # remaining lifetime (Myr)
                round(r_s_solar_units, 6),      # Schwarzschild radius (solar radii)
                round(L_solar_units, 3),        # Luminosity (solar)
                round(v_recession, 1),          # Recession velocity (km/s)
                round(doppler_factor, 4)        # Doppler factor
            ))
        
        return results
    
    # ============================================================
    # NUCLEAR AND PARTICLE PHYSICS
    # ============================================================
    @staticmethod
    def nuclear_particle(params: Dict[str, float]) -> List[Tuple[float, ...]]:
        """
        Solve nuclear and particle physics problems:
        - Nuclear decay (half-life)
        - Binding energy
        - Cross sections
        - Particle interactions
        """
        # Parameters
        half_life = np.clip(params.get('half_life', 10), 0.1, 1000)  # seconds
        initial_activity = np.clip(params.get('initial_activity', 1000), 1, 1e6)  # Bq
        mass_number = int(np.clip(params.get('mass_number', 56), 1, 300))
        atomic_number_nuclear = int(np.clip(params.get('atomic_number', 26), 1, 118))
        binding_energy_per_nucleon = np.clip(params.get('binding_energy', 8.5), 1, 10)  # MeV
        
        dt = 0.1
        steps = 30
        results = []
        
        # Constants
        lambda_decay = math.log(2) / half_life
        m_proton = 938.272  # MeV/c^2
        m_neutron = 939.565  # MeV/c^2
        mass_defect_factor = 1e-3  # MeV per nucleon
        
        for i in range(steps):
            t = i * dt
            
            # Radioactive decay
            N_remaining = initial_activity * math.exp(-lambda_decay * t)
            
            # Activity
            activity = N_remaining * lambda_decay
            
            # Binding energy total
            binding_energy_total = binding_energy_per_nucleon * mass_number
            
            # Mass defect (simplified)
            mass_defect = mass_defect_factor * mass_number
            
            # Cross section (simplified energy dependence)
            energy_beam = 0.1 + t * 0.05  # GeV
            cross_section = 0.1 / (energy_beam + 0.1)  # arbitrary units
            
            # Q-value for decay (simplified)
            q_value = 0.5 * binding_energy_per_nucleon * (mass_number / 10)
            
            results.append((
                round(t, 2),                    # time (seconds)
                round(activity, 1),             # Activity (Bq)
                round(N_remaining, 0),          # Remaining nuclei
                round(binding_energy_total, 2), # Binding energy (MeV)
                round(cross_section, 4),        # Cross section
                round(q_value, 3)               # Q-value (MeV)
            ))
        
        return results
    
    # ============================================================
    # MAP PROBLEM TYPES TO SOLVERS
    # ============================================================
    SOLVERS = {
        'mechanics': mechanics,
        'electromagnetism': electromagnetism,
        'quantum': quantum,
        'thermodynamics': thermodynamics,
        'waves': waves,
        'solid_state': solid_state,
        'atomic_molecular': atomic_molecular,
        'astrophysics': astrophysics,
        'nuclear_particle': nuclear_particle
    }
    
    # Metadata for each solver
    SOLVER_METADATA = {
        'mechanics': {
            'display_name': 'Classical Mechanics',
            'description': 'Projectile motion, forces, friction',
            'parameters': ['gravity', 'mass', 'initial_velocity_x', 'initial_velocity_y', 'angle', 'friction']
        },
        'electromagnetism': {
            'display_name': 'Electromagnetism',
            'description': 'Charged particle motion in electric/magnetic fields',
            'parameters': ['charge', 'field_strength', 'mass']
        },
        'quantum': {
            'display_name': 'Quantum Mechanics',
            'description': 'Quantum wavefunctions and probability',
            'parameters': ['energy', 'potential']
        },
        'thermodynamics': {
            'display_name': 'Thermodynamics',
            'description': 'Heat transfer and cooling',
            'parameters': ['initial_temp', 'ambient_temp', 'cooling_rate']
        },
        'waves': {
            'display_name': 'Wave Mechanics',
            'description': 'Wave propagation and interference',
            'parameters': ['amplitude', 'frequency', 'wavelength']
        },
        'solid_state': {
            'display_name': 'Solid State Physics',
            'description': 'Band structure, Fermi surfaces, phonons',
            'parameters': ['temperature', 'fermi_energy', 'band_gap', 'lattice_constant', 'electron_density']
        },
        'atomic_molecular': {
            'display_name': 'Atomic & Molecular Physics',
            'description': 'Energy levels, spectra, molecular vibrations',
            'parameters': ['atomic_number', 'principal_quantum', 'reduced_mass', 'bond_length', 'vibrational_quantum', 'rotational_quantum']
        },
        'astrophysics': {
            'display_name': 'Astrophysics',
            'description': 'Stellar evolution, black holes, cosmology',
            'parameters': ['stellar_mass', 'stellar_radius', 'luminosity', 'temperature', 'red_shift', 'distance']
        },
        'nuclear_particle': {
            'display_name': 'Nuclear & Particle Physics',
            'description': 'Radioactive decay, binding energy, cross sections',
            'parameters': ['half_life', 'initial_activity', 'mass_number', 'atomic_number', 'binding_energy']
        }
    }
    
    @classmethod
    def get_solver_list(cls) -> List[Dict[str, Any]]:
        """Get list of all available solvers with metadata"""
        return [
            {
                'id': solver_id,
                'display_name': cls.SOLVER_METADATA[solver_id]['display_name'],
                'description': cls.SOLVER_METADATA[solver_id]['description'],
                'parameters': cls.SOLVER_METADATA[solver_id]['parameters']
            }
            for solver_id in cls.SOLVERS.keys()
        ]
    
    @classmethod
    def solve(cls, problem_type: str, params: Dict[str, float]) -> Dict[str, Any]:
        """Main entry point - solves any physics problem"""
        if problem_type not in cls.SOLVERS:
            problem_type = 'mechanics'
        
        numerical_data = cls.SOLVERS[problem_type](params)
        
        # Generate sonification frequencies (velocity → audio)
        sonification = []
        for step in numerical_data:
            # Use the last numeric value in each step as velocity proxy
            velocity = abs(step[-1]) if len(step) > 1 else 0
            # Scale to audible range (220-2000 Hz)
            freq = np.clip(220 + velocity * 20, 100, 2000)
            sonification.append(round(freq, 2))
        
        # Generate column labels based on solver type
        column_labels = {
            'mechanics': ['Time (s)', 'X (m)', 'Y (m)', 'Velocity (m/s)'],
            'electromagnetism': ['Time (s)', 'X (m)', 'Y (m)', 'Velocity (m/s)'],
            'quantum': ['Time (s)', 'Position', 'Probability x 10', 'Velocity'],
            'thermodynamics': ['Time (s)', 'Temperature (K)', 'Energy', 'Rate'],
            'waves': ['Time (s)', 'X (m)', 'Displacement', 'Velocity'],
            'solid_state': ['Index', 'Energy (eV)', 'Fermi-Dirac', 'DOS (arb)', 'Fermi Velocity (km/s)'],
            'atomic_molecular': ['Index', 'Electronic (eV)', 'Vibrational (eV)', 'Rotational (eV)', 'Total (eV)', 'Wavelength (nm)'],
            'astrophysics': ['Time (Myr)', 'Remaining (Myr)', 'Rs (Solar)', 'Luminosity (Solar)', 'Recession (km/s)', 'Doppler Factor'],
            'nuclear_particle': ['Time (s)', 'Activity (Bq)', 'Nuclei', 'Binding (MeV)', 'Cross Section', 'Q-value (MeV)']
        }
        
        return {
            'numerical_data': numerical_data,
            'sonification_frequencies': sonification,
            'column_labels': column_labels.get(problem_type, [f'Column_{i}' for i in range(len(numerical_data[0]) if numerical_data else 0)]),
            'solver_type': problem_type,
            'metadata': cls.SOLVER_METADATA.get(problem_type, {})
        }