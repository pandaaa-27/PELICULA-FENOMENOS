import numpy as np
import numpy as np

import sympy as sp
import numpy as np

def get_table_data(R, rho, mu):
    # Generar 6 deltas representativos que muestren cómo sube el error
    # Por ejemplo: Empezamos muy chico y subimos hasta cruzar el ~5% - 10%
    deltas = np.array([0.0001, 0.001, 0.005, 0.010, 0.020, 0.030])
    
    g = 9.81
    rows = []
    
    for d in deltas:
        a_val = 1 + d/R
        # exact mass flow
        f_a = 4 * a_val**4 * np.log(a_val) - (3 * a_val**4 - 4 * a_val**2 + 1)
        m_e = (np.pi * rho**2 * g * R**4 / (8 * mu)) * f_a
        
        # simplified mass flow
        m_a = (2 * np.pi * R * rho**2 * g * d**3) / (3 * mu)
        
        # error
        e_rel = abs(m_e - m_a) / m_e * 100 if m_e > 0 else 0
        
        rows.append({
            'delta': f"{d:.4f}",
            'm_exacto': f"{m_e:.5f}",
            'm_simplificado': f"{m_a:.5f}",
            'error': f"{e_rel:.2f}"
        })
        
    return rows

def generate_comparison_data(R, rho, mu, num_points=100):
    # delta ranges from 0 to 0.5 * R for good visualization of the error curve
    delta_array = np.linspace(0, 0.5 * R, num_points)
    
    # avoiding delta=0 exactly for log issues with a=1 error calculation if needed, 
    # but a=1 makes log(1)=0 which is fine.
    
    a_array = 1 + delta_array / R
    g = 9.81
    
    # exact mass flow term
    term_a = 4 * a_array**4 * np.log(a_array) - (3 * a_array**4 - 4 * a_array**2 + 1)
    m_exact = (np.pi * rho**2 * g * R**4 / (8 * mu)) * term_a
    
    # approximate mass flow term (flat plate)
    m_approx = (2 * np.pi * R * rho**2 * g * delta_array**3) / (3 * mu)
    
    # calculate percentage error
    error = np.zeros_like(m_exact)
    mask = m_exact > 1e-12  # avoid division by zero
    error[mask] = np.abs((m_approx[mask] - m_exact[mask]) / m_exact[mask]) * 100
    
    return delta_array, m_exact, m_approx, error
