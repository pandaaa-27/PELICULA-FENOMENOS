import numpy as np

g = 9.81  # m/s^2

def calculate_radii(R: float, delta: float):
    """
    Calcula el radio exterior total y la relación de radios.
    """
    aR = R + delta
    a = aR / R
    return aR, a

def calculate_mass_flow(rho: float, mu: float, R: float, a: float) -> float:
    """
    Calcula el flujo másico m_punto [kg/s] en la película descendente.
    """
    term1 = (np.pi * (rho**2) * g * (R**4)) / (8 * mu)
    term2 = 4 * (a**4) * np.log(a) - (3 * (a**4) - 4 * (a**2) + 1)
    m_punto = term1 * term2
    return m_punto

def calculate_velocity_profile(r: np.ndarray, rho: float, mu: float, R: float, a: float) -> np.ndarray:
    """
    Calcula el perfil de velocidad vz(r) [m/s] en la película.
    r debe estar en el rango [R, aR].
    """
    vz = (rho * g * (R**2) / (4 * mu)) * (1 - (r/R)**2 + 2 * (a**2) * np.log(r/R))
    # Para evitar posibles valores minúsculos negativos por precisión en r=R
    vz = np.maximum(vz, 0)
    return vz

def calculate_max_velocity(rho: float, mu: float, R: float, a: float, aR: float) -> float:
    """
    Calcula la velocidad máxima vz_max [m/s], que ocurre en r = aR.
    """
    # Pasamos aR como escalar, pero el cálculo funciona igual
    vz_max = calculate_velocity_profile(aR, rho, mu, R, a)
    return float(vz_max)

def calculate_average_velocity(m_punto: float, rho: float, R: float, a: float) -> float:
    """
    Calcula la velocidad media vz_prom [m/s] a partir del flujo másico.
    """
    # A = pi * (aR^2 - R^2) = pi * R^2 * (a^2 - 1)
    area = np.pi * (R**2) * (a**2 - 1)
    if area <= 0:
        return 0.0
    vz_prom = m_punto / (rho * area)
    return float(vz_prom)
