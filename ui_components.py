import plotly.graph_objects as go
import numpy as np
from nicegui import ui
import matplotlib.pyplot as plt
import analysis as ana

def create_header():
    with ui.row().classes('w-full items-center justify-between p-4 bg-[#1c1926] border-b border-purple-500/50'):
        with ui.column().classes('gap-0'):
            ui.label('Simulador de Flujo en Película Cilíndrica').classes('text-2xl font-bold text-white')
            ui.label('Fenómenos de Transporte I · UNMSM · Ejercicio 2B6').classes('text-sm text-purple-300/70 font-medium')
        ui.label('UNMSM').classes('bg-purple-600 text-white px-3 py-1 rounded-full text-sm font-semibold tracking-wider')
        
def create_metric_card(title: str, value: str, color_hex: str, icon_name: str):
    with ui.card().classes('w-full').style(f'border-left: 4px solid {color_hex}; background-color: #1c1926;'):
        with ui.row().classes('items-center gap-3'):
            ui.icon(icon_name, size='s').style(f'color: {color_hex}')
            with ui.column().classes('gap-0'):
                ui.label(title).classes('text-xs text-gray-400 font-semibold uppercase')
                ui.label(value).classes('text-lg font-bold text-white')

def create_metric_card_mini(title: str, value: str, color_hex: str, icon_name: str):
    with ui.row().classes('items-center gap-4 bg-[#1c1926] px-6 py-3 rounded-lg border border-purple-900/30 shadow-md transition-all hover:border-purple-500/50'):
        ui.icon(icon_name, size='m').style(f'color: {color_hex}')
        with ui.column().classes('gap-0'):
            ui.label(title).classes('text-[10px] text-gray-500 font-bold uppercase tracking-widest')
            ui.label(value).classes('text-xl font-black text-white')

@ui.refreshable
def create_top_results_bar(m_punto: float, vz_prom: float, a: float):
    with ui.row().classes('w-full max-w-[1400px] mx-auto p-4 justify-center gap-6'):
        create_metric_card_mini('Flujo Másico [kg/s]', f"{m_punto:.5f}", '#f472b6', 'water_drop')
        create_metric_card_mini('Velocidad Media [m/s]', f"{vz_prom:.5f}", '#a78bfa', 'speed')
        create_metric_card_mini('Relación de Radios (a)', f"{a:.4f}", '#fbbf24', 'api')

def create_physical_plot(R: float, aR: float, r_array: np.ndarray, vz_array: np.ndarray):
    # Generar malla para los cilindros
    theta = np.linspace(0, 2*np.pi, 30)
    z = np.linspace(0, 10, 2)
    THETA, Z = np.meshgrid(theta, z)
    
    # Cilindro Interno (Tubo Sólido)
    X_tube = R * np.cos(THETA)
    Y_tube = R * np.sin(THETA)
    
    # Cilindro Externo (Película Líquida)
    X_film = aR * np.cos(THETA)
    Y_film = aR * np.sin(THETA)
    
    fig = go.Figure()
    
    # Superficie del tubo (gris sólido)
    fig.add_trace(go.Surface(
        x=X_tube, y=Y_tube, z=Z,
        colorscale=[[0, '#424242'], [1, '#424242']],
        showscale=False,
        name='Tubo Sólido',
        opacity=1.0
    ))
    
    # Superficie de la película (orquidea rosada traslúcida)
    fig.add_trace(go.Surface(
        x=X_film, y=Y_film, z=Z,
        colorscale=[[0, '#f472b6'], [1, '#f472b6']],
        showscale=False,
        name='Película Líquida',
        opacity=0.4
    ))
    
    # Vectores de velocidad 3D (Conos)
    if vz_array is not None and len(vz_array) > 0:
        # Tomar 4 radios y 4 ángulos para los vectores
        num_r = 3
        num_theta = 6
        num_z = 3
        
        r_vals = np.linspace(R + (aR-R)*0.2, aR - (aR-R)*0.1, num_r)
        theta_vals = np.linspace(0, 2*np.pi, num_theta, endpoint=False)
        z_vals = np.linspace(2, 8, num_z)
        
        c_x, c_y, c_z, u, v, w = [], [], [], [], [], []
        
        for rv in r_vals:
            vz_local = np.interp(rv, r_array, vz_array)
            for tv in theta_vals:
                for zv in z_vals:
                    c_x.append(rv * np.cos(tv))
                    c_y.append(rv * np.sin(tv))
                    c_z.append(zv)
                    u.append(0)
                    v.append(0)
                    w.append(-1.0) # Dirección constante hacia abajo
        
        fig.add_trace(go.Cone(
            x=c_x, y=c_y, z=c_z,
            u=u, v=v, w=w,
            sizemode="absolute",
            sizeref=0.1, # Muy pequeño y constante
            colorscale=[[0, '#00d4aa'], [1, '#00d4aa']],
            showscale=False,
            name='Vectores Velocidad'
        ))
    
    # Configuración de escena 3D
    fig.update_layout(
        title="Representación Física 3D",
        template="plotly_dark",
        paper_bgcolor="#0f1117",
        plot_bgcolor="#0f1117",
        margin=dict(l=0, r=0, t=40, b=0),
        height=400,
        scene=dict(
            xaxis=dict(title='X [m]', range=[-aR*1.5, aR*1.5], showgrid=True, gridcolor="#333"),
            yaxis=dict(title='Y [m]', range=[-aR*1.5, aR*1.5], showgrid=True, gridcolor="#333"),
            zaxis=dict(title='Altura Z [m]', range=[0, 10], showgrid=True, gridcolor="#333"),
            aspectmode='manual',
            aspectratio=dict(x=1, y=1, z=1.5),
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.2)
            )
        ),
        showlegend=False
    )
    return fig

def create_velocity_profile_plot(R: float, aR: float, r_array: np.ndarray, vz_array: np.ndarray):
    fig = go.Figure()
    
    # Tubo (gris) - v=0
    fig.add_trace(go.Scatter(
        x=[0, R], y=[0, 0],
        mode='lines',
        fill='tozeroy',
        fillcolor='rgba(66, 66, 66, 0.5)',
        line=dict(color='#424242', width=2),
        name='Tubo Sólido (v=0)'
    ))
    
    # Perfil real (azul)
    fig.add_trace(go.Scatter(
        x=r_array, y=vz_array,
        mode='lines',
        fill='tozeroy',
        fillcolor='rgba(79, 142, 247, 0.5)',
        line=dict(color='#4f8ef7', width=3),
        name='Perfil Vz(r)'
    ))
    
    # Punto rojo (r=R)
    fig.add_trace(go.Scatter(
        x=[R], y=[0],
        mode='markers',
        marker=dict(color='#f74f4f', size=10, symbol='circle'),
        name='No-slip (v=0)'
    ))
    
    # Punto verde (r=aR)
    vz_max = np.max(vz_array) if vz_array is not None and len(vz_array) > 0 else 0
    fig.add_trace(go.Scatter(
        x=[aR], y=[vz_max],
        mode='markers',
        marker=dict(color='#00d4aa', size=10, symbol='circle'),
        name='Interfase (V_max)'
    ))
    
    fig.update_layout(
        title="Perfil Matemático de Velocidad",
        xaxis_title="Radio r [m]",
        yaxis_title="Velocidad Vz [m/s]",
        template="plotly_dark",
        paper_bgcolor="#0f1117",
        plot_bgcolor="#0f1117",
        xaxis=dict(range=[0, aR + 0.01], showgrid=True, gridcolor="#333"),
        yaxis=dict(showgrid=True, gridcolor="#333"),
        margin=dict(l=40, r=40, t=50, b=40),
        height=400,
        showlegend=False
    )
    return fig

def create_equations_section():
    equations_html = r"""
    <div style="color: #bbc1cc; background: #1a1f2e; padding: 20px; border-radius: 8px;">
        <h3 style="margin-top: 0; color: #fff;">Ecuaciones del Modelo</h3>
        <p><strong>Perfil de Velocidad:</strong></p>
        <div style="font-size: 1.2em; text-align: center; margin: 10px 0;">
            $$ v_z(r) = \frac{\rho g R^2}{4\mu} \left[ 1 - \left(\frac{r}{R}\right)^2 + 2a^2 \ln\left(\frac{r}{R}\right) \right] $$
        </div>
        <p><strong>Flujo Másico:</strong></p>
        <div style="font-size: 1.2em; text-align: center; margin: 10px 0;">
            $$ \dot{m} = \frac{\pi \rho^2 g R^4}{8\mu} \left[ 4a^4 \ln(a) - (3a^4 - 4a^2 + 1) \right] $$
        </div>
        <p><strong>Velocidad Media:</strong></p>
        <div style="font-size: 1.2em; text-align: center; margin: 10px 0;">
            $$ \langle v_z \rangle = \frac{\dot{m}}{\rho \cdot \text{Área}} $$
        </div>
        Donde \( a = \frac{R + \delta}{R} \), \( \text{Área} = \pi R^2 (a^2 - 1) \) y \( r \in [R, R+\delta] \).
    </div>
    """
    ui.html(equations_html)

@ui.refreshable
def create_taylor_analysis_section(R: float, rho: float, mu: float):
    with ui.column().classes('w-full max-w-[1400px] mx-auto p-4 gap-6'):
        ui.label('Análisis Analítico y Comparación').classes('text-2xl font-black text-white text-center w-full mb-4 mt-8')
        
        with ui.row().classes('w-full gap-6 items-stretch'):
            # Columna Izquierda: Fórmula y Tabla
            with ui.column().classes('w-full md:w-[48%] bg-[#1a1f2e] p-6 rounded-xl shadow-lg border border-gray-800'):
                ui.label('Fórmula Simplificada y Tabla de Análisis').classes('text-xl font-bold text-blue-400 mb-4')
                ui.label(f'Al aplicar la expansión en Serie de Taylor cuando δ → 0, usando tus variables actuales (ρ={rho:.0f}, μ={mu:.2f} y R={R:.3f}):').classes('text-gray-400 mb-2 text-sm')
                
                with ui.card().classes('w-full bg-[#0f1117] border border-gray-700 p-4 mb-6'):
                    ui.markdown(r"$$ \dot{m} = \frac{2\pi R \rho^2 g \delta^3}{3\mu} $$").classes('text-center text-xl text-teal-400 w-full')
                
                ui.label('Impacto del Espesor de Película').classes('text-lg font-bold text-white mb-2')
                
                columns = [
                    {'name': 'delta', 'label': 'Espesor δ (m)', 'field': 'delta', 'align': 'left'},
                    {'name': 'm_exacto', 'label': 'ṁ exacto', 'field': 'm_exacto', 'align': 'center'},
                    {'name': 'm_simplificado', 'label': 'ṁ Taylor', 'field': 'm_simplificado', 'align': 'center'},
                    {'name': 'error', 'label': 'Error (%)', 'field': 'error', 'align': 'center'},
                ]
                
                # Usando los valores dinámicos configurados por el usuario
                rows = ana.get_table_data(R, rho, mu)
                
                ui.table(columns=columns, rows=rows, row_key='delta').classes('w-full bg-[#0f1117] text-white border border-gray-700')

            # Columna Derecha: Gráficas Matplotlib
            with ui.column().classes('w-full md:w-[48%] bg-[#1a1f2e] p-6 rounded-xl shadow-lg border border-gray-800'):
                ui.label('Comparación de Flujo Másico y Error').classes('text-xl font-bold text-orange-400 mb-4')
                ui.label('Modelo Cilíndrico Exacto vs Modelo Plana (Flujo en Pared).').classes('text-gray-400 mb-2 text-sm')
                
                delta_arr, m_exact, m_approx, error = ana.generate_comparison_data(R, rho, mu)
                
                with ui.pyplot(figsize=(6, 8), facecolor='#1a1f2e') as plot:
                    plt.style.use('dark_background')
                    fig = plot.fig
                    
                    # Interpolar para encontrar punto crítico (5%)
                    if error[-1] >= 5.0:
                        cruce_idx = np.where(error >= 5.0)[0][0]
                        d_cruce = delta_arr[cruce_idx]
                    else:
                        d_cruce = None
                        
                    ratio_arr = delta_arr / R
                    
                    # Subplot superior: Flujos
                    ax1 = fig.add_subplot(2, 1, 1)
                    ax1.plot(ratio_arr, m_exact, label='m_exacto (Cilíndrico)', color='#a78bfa', linewidth=2)
                    ax1.plot(ratio_arr, m_approx, label='m_simplificado (Taylor)', color='#f472b6', linestyle='--', linewidth=2)
                    ax1.set_title(r'Gráfica A: Comparación de curvas vs $\delta$', color='white')
                    ax1.set_ylabel('Flujo Másico ṁ [kg/s]')
                    ax1.legend(loc='upper left', frameon=False)
                    ax1.grid(color='#333', linestyle='--', linewidth=0.5)
                    
                    # Subplot inferior: Error Relativo
                    ax2 = fig.add_subplot(2, 1, 2)
                    ax2.plot(ratio_arr, error, color='#ec4899', linewidth=2)
                    ax2.set_title(r'Gráfica B: Evolución del Error Relativo (%) vs $\delta$', color='white')
                    ax2.set_xlabel('Relación Adimensional δ/R')
                    ax2.set_ylabel('Error (%)')
                    
                    if d_cruce:
                        rcruce = d_cruce / R
                        ax2.axhline(y=5, color='yellow', linestyle=':', label='Límite 5% de Error')
                        ax2.plot(rcruce, 5, 'yo', markersize=8)
                        ax2.annotate(rf'Cruza 5% en $\delta \approx {d_cruce:.4f}$ m',
                                     xy=(rcruce, 5), xytext=(rcruce - 0.05, 12 if np.max(error)>15 else 8),
                                     arrowprops=dict(facecolor='yellow', shrink=0.05),
                                     color='yellow', fontweight='bold')
                                     
                    ax2.legend()
                    ax2.grid(color='#333', linestyle='--', linewidth=0.5)
                    
                    # Rellenar área bajo la curva de error
                    ax2.fill_between(ratio_arr, 0, error, color='#ec4899', alpha=0.3)
                    
                    plt.tight_layout()
                    
        # Forzar el renderizado de MathJax tras actualizar el contenido
        ui.run_javascript('setTimeout(() => { if (window.MathJax) MathJax.typesetPromise() }, 100);')

def create_footer():
    ui.label('Nota: Modelo físico ideal asumiendo flujo laminar descendente en estado estacionario (Newtoniano).').classes('w-full text-center text-xs text-gray-500 mt-4 p-4')

