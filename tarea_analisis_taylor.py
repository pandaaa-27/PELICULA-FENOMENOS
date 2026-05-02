import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

def demostracion_simbolica():
    print("==========================================================================")
    print(" FÓRMULA SIMPLIFICADA PARA ESPESOR MÍNIMO (PELÍCULA DELGADA)")
    print("==========================================================================\n")
    
    print("[*] Al aplicar la expansión en Serie de Taylor cuando \delta -> 0,")
    print("    la Ecuación de Flujo Másico Cilíndrico se reduce a la fórmula")
    print("    de Flujo de Pared Plana Vertical:\n")
    print("    m_dot = (2 * pi * R * rho^2 * g * delta^3) / (3 * mu)\n")


def tabla_y_graficas():
    print("==========================================================================")
    print(" TABLA COMPARATIVA DE FLUJO MÁSICO")
    print("==========================================================================\n")
    
    # Parámetros físicos solicitados
    rho_val = 1000.0  # kg/m^3 
    mu_val = 0.27     # Pa.s 
    R_val = 0.05      # m (5 cm)
    g_val = 9.81      # m/s^2
    
    # Delta deseados 
    deltas = np.array([0.0001, 0.001, 0.005, 0.010, 0.020, 0.030])
    
    def calc_exact(d):
        a_val = 1 + d/R_val
        f_a = 4 * a_val**4 * np.log(a_val) - (3 * a_val**4 - 4 * a_val**2 + 1)
        return (np.pi * rho_val**2 * g_val * R_val**4 / (8 * mu_val)) * f_a
        
    def calc_approx(d):
        return (2 * np.pi * R_val * rho_val**2 * g_val * d**3) / (3 * mu_val)
        
    print(f"{'Espesor d (m)':<15} | {'m_exacto (kg/s)':<20} | {'m_simplificado (kg/s)':<25} | {'Error Relativo (%)':<20}")
    print("-" * 90)
    
    for d in deltas:
        m_e = calc_exact(d)
        m_a = calc_approx(d)
        e_rel = abs(m_e - m_a) / m_e * 100 if m_e > 0 else 0
        print(f"{d:<15.4f} | {m_e:<20.6f} | {m_a:<25.6f} | {e_rel:<20.2f}")
        
    print("\n[*] Abriendo Gráficas de Validación con Matplotlib...\n")
    
    d_smooth = np.linspace(0.0001, 0.03, 500)
    m_exact_arr = calc_exact(d_smooth)
    m_approx_arr = calc_approx(d_smooth)
    error_arr = np.abs(m_exact_arr - m_approx_arr) / m_exact_arr * 100
    
    # Interpolar para encontrar punto crítico
    if error_arr[-1] >= 5.0:
        cruce_idx = np.where(error_arr >= 5.0)[0][0]
        d_cruce = d_smooth[cruce_idx]
    else:
        d_cruce = None
    
    plt.style.use('dark_background')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 10))
    fig.suptitle('Validación: Modelo Cilíndrico vs Pared Plana Simplificado', fontsize=14, fontweight='bold')
    
    # Gráfica A
    ax1.plot(d_smooth, m_exact_arr, label='m_exacto (Cilíndrico)', color='#4f8ef7', lw=2)
    ax1.plot(d_smooth, m_approx_arr, label='m_simplificado (Pared Plana)', color='#00d4aa', ls='--', lw=2)
    ax1.set_title(r'Gráfica A: Comparación de curvas de flujo másico vs $\delta$', fontsize=12)
    ax1.set_ylabel('Flujo Másico [kg/s]')
    ax1.legend()
    ax1.grid(color='#333', ls='--', alpha=0.5)
    
    # Gráfica B
    ax2.plot(d_smooth, error_arr, color='#f74f4f', lw=2)
    ax2.set_title(r'Gráfica B: Evolución del Error Relativo (%) vs $\delta$', fontsize=12)
    ax2.set_xlabel(r'Espesor $\delta$ [m]')
    ax2.set_ylabel('Error Relativo [%]')
    
    if d_cruce:
        ax2.axhline(y=5, color='yellow', linestyle=':', label='Límite de confiabilidad (5%)')
        ax2.plot(d_cruce, 5, 'yo', markersize=8)
        ax2.annotate(rf'Error > 5% en $\delta \approx {d_cruce:.4f}$ m',
                     xy=(d_cruce, 5), xytext=(d_cruce - 0.005, 12 if np.max(error_arr)>15 else 8),
                     arrowprops=dict(facecolor='yellow', shrink=0.05),
                     color='yellow', fontweight='bold')
                     
    ax2.fill_between(d_smooth, 0, error_arr, color='#f74f4f', alpha=0.3)
    ax2.grid(color='#333', ls='--', alpha=0.5)
    ax2.legend()
    
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    demostracion_simbolica()
    tabla_y_graficas()
