from nicegui import ui
import numpy as np
import backend as bk
from ui_components import (
    create_header, create_metric_card, create_physical_plot,
    create_velocity_profile_plot, create_equations_section, create_footer, go,
    create_top_results_bar, create_taylor_analysis_section
)

class AppState:
    def __init__(self):
        self.rho = 1000.0
        self.mu = 0.10
        self.R = 0.050
        self.delta = 0.015

app_state = AppState()

@ui.page('/')
def index():
    # Estilizado global con dark theme (Lavender/Premium)
    ui.add_head_html('<style>body { background-color: #121019; color: white; font-family: "Inter", "Roboto", sans-serif; }</style>')
    ui.add_head_html('<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script><script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>')
    ui.dark_mode().enable()
    
    create_header()
    
    # Barra de resultados en la parte superior
    aR_init, a_init = bk.calculate_radii(app_state.R, app_state.delta)
    m_punto_init = bk.calculate_mass_flow(app_state.rho, app_state.mu, app_state.R, a_init)
    vz_prom_init = bk.calculate_average_velocity(m_punto_init, app_state.rho, app_state.R, a_init)
    create_top_results_bar(m_punto_init, vz_prom_init, a_init)
    
    with ui.tabs().classes('w-full bg-[#1c1926] text-purple-200/60 shadow-lg') as tabs:
        tab_sim = ui.tab('Simulador de Flujo').classes('font-bold tracking-wider active:text-purple-400')
        tab_ana = ui.tab('Análisis de Precisión (Taylor)').classes('font-bold tracking-wider active:text-pink-400')
        
    with ui.tab_panels(tabs, value=tab_sim).classes('w-full bg-transparent p-0'):
        with ui.tab_panel(tab_sim):
            with ui.row().classes('w-full max-w-[1400px] mx-auto gap-6 p-4 items-stretch'):
                
                # PANEL IZQUIERDO: CONTROLES
                with ui.column().classes('w-full md:w-[32%] bg-[#1c1926] p-6 rounded-xl shadow-xl border border-purple-900/30 mb-auto'):
                    ui.label('Parámetros de Entrada').classes('text-xl font-bold text-white mb-4 border-b border-purple-500/20 pb-2')
                    
                    with ui.column().classes('w-full gap-4'):
                        # Densidad
                        with ui.row().classes('w-full items-center gap-2'):
                            ui.icon('water_drop', color='#f472b6').classes('text-xl')
                            ui.label('Densidad ρ [kg/m³]').classes('text-sm text-purple-200/80 flex-grow cursor-help').tooltip('Densidad del fluido')
                            ui.label().bind_text_from(app_state, 'rho', backward=lambda v: f"{v:.0f}").classes('font-bold text-white')
                        ui.slider(min=800, max=1500, step=1).bind_value(app_state, 'rho').classes('w-full').props('color="pink"').on('update:model-value', lambda e: trigger_update())
                        
                        # Viscosidad
                        with ui.row().classes('w-full items-center gap-2 mt-2'):
                            ui.icon('waves', color='#a78bfa').classes('text-xl')
                            ui.label('Viscosidad μ [Pa·s]').classes('text-sm text-purple-200/80 flex-grow cursor-help').tooltip('Viscosidad dinámica del fluido')
                            ui.label().bind_text_from(app_state, 'mu', backward=lambda v: f"{v:.2f}").classes('font-bold text-white')
                        ui.slider(min=0.01, max=1.00, step=0.01).bind_value(app_state, 'mu').classes('w-full').props('color="purple"').on('update:model-value', lambda e: trigger_update())
                        
                        # Radio del tubo
                        with ui.row().classes('w-full items-center gap-2 mt-2'):
                            ui.icon('radio_button_unchecked', color='#fbbf24').classes('text-xl')
                            ui.label('Radio R [m]').classes('text-sm text-purple-200/80 flex-grow cursor-help').tooltip('Radio exterior del sólido')
                            ui.label().bind_text_from(app_state, 'R', backward=lambda v: f"{v:.3f}").classes('font-bold text-white')
                        ui.number(min=0.010, max=0.500, step=0.001, format='%.3f').bind_value(app_state, 'R').classes('w-full').props('filled dark color="amber"').on('update:model-value', lambda e: trigger_update())
                        
                        # Espesor de película
                        with ui.row().classes('w-full items-center gap-2 mt-4'):
                            ui.icon('straighten', color='#f43f5e').classes('text-xl')
                            ui.label('Espesor δ [m]').classes('text-sm text-purple-200/80 flex-grow cursor-help').tooltip('Espesor de la película líquida sobre el tubo')
                            ui.label().bind_text_from(app_state, 'delta', backward=lambda v: f"{v:.3f}").classes('font-bold text-white')
                        ui.slider(min=0.001, max=0.050, step=0.001).bind_value(app_state, 'delta').classes('w-full').props('color="rose"').on('update:model-value', lambda e: trigger_update())
                        
                    def reset():
                        app_state.rho = 1000.0
                        app_state.mu = 0.27
                        app_state.R = 0.050
                        app_state.delta = 0.015
                        trigger_update()
                        
                    ui.button('Resetear valores', icon='refresh', on_click=reset).classes('w-full mt-6 bg-purple-900/40 hover:bg-purple-800/60 text-purple-100 border border-purple-500/30')
                    
                    ui.separator().classes('my-6 bg-purple-900/40')
                    ui.label('Métricas Calculadas').classes('text-lg font-bold text-white mb-2')
                    
                    # Contenedor para tarjetas métricas
                    @ui.refreshable
                    def metric_cards():
                        aR, a = bk.calculate_radii(app_state.R, app_state.delta)
                        m_punto = bk.calculate_mass_flow(app_state.rho, app_state.mu, app_state.R, a)
                        vz_max = bk.calculate_max_velocity(app_state.rho, app_state.mu, app_state.R, a, aR)
                        
                        with ui.column().classes('w-full gap-3 transition-all'):
                            if vz_max <= 1e-6:
                                with ui.row().classes('w-full bg-rose-900/50 p-2 rounded items-center gap-2 border border-rose-500/50'):
                                    ui.icon('warning', color='white').classes('text-lg')
                                    ui.label('Advertencia: Velocidad casi nula').classes('text-rose-200 font-semibold text-xs')
                                    
                            create_metric_card('Flujo Másico ṁ [kg/s]', f"{m_punto:.4f}", '#f472b6', 'water_drop')
                            create_metric_card('Velocidad Máxima [m/s]', f"{vz_max:.4f}", '#a78bfa', 'speed')
                            create_metric_card('Relación de Radios (a)', f"{a:.3f}", '#fbbf24', 'api')
                    
                    metric_cards()

                # PANEL DERECHO: VISUALIZACIONES
                with ui.column().classes('w-full md:w-[65%] gap-6 mb-auto'):
                    # Contenedor para gráficas en paralelo
                    with ui.row().classes('w-full gap-4 items-stretch'):
                        with ui.card().classes('flex-grow md:w-[48%] bg-[#1c1926] border border-purple-900/30 p-4 shadow-lg'):
                            ui.label('Representación Física').classes('text-sm font-semibold text-pink-400 uppercase tracking-wider mb-2')
                            plot1 = ui.plotly(go.Figure()).classes('w-full h-[400px]')
                        
                        with ui.card().classes('flex-grow md:w-[48%] bg-[#1c1926] border border-purple-900/30 p-4 shadow-lg'):
                            ui.label('Perfil de Velocidad').classes('text-sm font-semibold text-purple-400 uppercase tracking-wider mb-2')
                            plot2 = ui.plotly(go.Figure()).classes('w-full h-[400px]')
                            
                    def trigger_update():
                        """Refresca las cards y actualiza las gráficas usando los valores actualles del state."""
                        metric_cards.refresh()
                        
                        aR, a = bk.calculate_radii(app_state.R, app_state.delta)
                        m_punto = bk.calculate_mass_flow(app_state.rho, app_state.mu, app_state.R, a)
                        vz_prom = bk.calculate_average_velocity(m_punto, app_state.rho, app_state.R, a)
                        
                        create_top_results_bar.refresh(m_punto, vz_prom, a)
                        create_taylor_analysis_section.refresh(app_state.R, app_state.rho, app_state.mu)
                        
                        # Ensure correct domain constraints 
                        r_arr = np.linspace(app_state.R, aR, 100)
                        vz_arr = bk.calculate_velocity_profile(r_arr, app_state.rho, app_state.mu, app_state.R, a)
                        
                        fig1 = create_physical_plot(app_state.R, aR, r_arr, vz_arr)
                        plot1.update_figure(fig1)
                        
                        fig2 = create_velocity_profile_plot(app_state.R, aR, r_arr, vz_arr)
                        plot2.update_figure(fig2)

                    # Ejecutar update inicial
                    trigger_update()
                    
                    # Ecuaciones LaTeX
                    create_equations_section()
            
        with ui.tab_panel(tab_ana):
            create_taylor_analysis_section(app_state.R, app_state.rho, app_state.mu)
            
    create_footer()

if __name__ in {'__main__', '__mp_main__'}:
    ui.run(title="Simulador Fenómenos - 2B6", port=8081, reload=False, dark=True)
