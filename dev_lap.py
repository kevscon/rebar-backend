import math
from config import props_path
from unit_conversion import return_ft_in
from rebar import RebarLayout

def calc_cb(bar_diameter: float, cover: float, spacing: float):
    """
    Calculates c_b value (in).

    Parameters:
    - bar_diameter: Diameter of rebar (in).
    - cover: Distance from face of concrete to edge of rebar (in).
    - spacing: Center-to-center spacing of rebar (in).
    """
    return min(bar_diameter / 2 + cover, spacing / 2)

def calc_lambda(conc_density):
    """
    Parameters:
    - conc_density: Concrete density (pcf).

    Returns:
    - lambda: Concrete density modification factor.
    """
    return min(max(7.5 * conc_density / 1000, 0.75), 1)

def calc_lambda_cf(bar_diameter, spacing, cover, epoxy_coat):
        """
        Calculates coating factor for tension devlopment length.

        Parameters:
        - d_b: Diameter of rebar (in).
        - spacing: Spacing of rebar (in).
        - cover: Clear cover from face of concrete to rebar (in).
        - epoxy_coat: Is rebar epoxy coated? (True/False).
        """
        if epoxy_coat == False:
            lambda_cf = 1
        else:
            clear_spacing = spacing - bar_diameter
            if cover < 3 * bar_diameter or clear_spacing < 6 * bar_diameter:
                lambda_cf = 1.5
            else:
                lambda_cf = 1.2
        return lambda_cf

def calc_lambda_rc(bar_diameter, c_b):
    """
    Calculates confinement factor for tension development length.
    """
    return min(max(bar_diameter / c_b, 0.4), 1)

def calc_lambda_rl(top_bar, f_c):
    """
    Calculates factor for bars cast 12" below face of concrete.
    """
    if top_bar == True:
        return 1.3
    elif f_c > 10:
        return 1.3
    else:
        return 1

def calc_lambda_cw(epoxy_coat):
    """
    Calculates coating factor for hook devlopment length.
    """
    if epoxy_coat == True:
        return 1.2
    else:
        return 1

def calc_l_db(bar_diameter, f_c, f_y):
    return 2.4 * bar_diameter * f_y / math.sqrt(f_c)

def calc_l_hdb(bar_diameter, f_c, f_y):
    return 38 * bar_diameter / 60 * (f_y / math.sqrt(f_c))

class ConcreteBeam:
    def __init__(self, bar_size: str, spacing: float, cover: float, f_c: float, f_y: float, conc_density: float):
        """
        Base class for concrete beam.
        
        Parameters:
        - bar_size: Standard bar size label (#).
        - spacing: Center-to-center spacing of rebar (in).
        - cover: Distance from concrete face to edge of reinforcing bar (in).
        - f_c: Compressive strength of concrete (ksi).
        - f_y: Yield strength of reinforcement (ksi).
        - conc_density: Concrete density (pcf).

        Initialized properties:
        - f_y: Yield strength of steel (ksi).
        - lambda: Concrete density modification factor.
        - c_b: (in).
        """

        self.spacing = spacing
        self.cover = cover
        self.f_c = f_c
        self.f_y = f_y
        self.conc_density = conc_density
        rebar = RebarLayout(bar_size, props_path)
        self.bar_diameter = rebar.bar_diameter
        self.bar_area = rebar.bar_area

class RebarDevLap:

    def __init__(self, beam_instance, epoxy_coat=False, top_bar=False, lambda_er=1):
        self.bar_diameter = beam_instance.bar_diameter
        self.f_c = beam_instance.f_c
        self.f_y = beam_instance.f_y
        self.spacing = beam_instance.spacing
        self.cover = beam_instance.cover
        self.epoxy_coat = epoxy_coat
        self.top_bar = top_bar
        self.c_b = calc_cb(self.bar_diameter, self.cover, self.spacing)

        self.lambda_ = calc_lambda(beam_instance.conc_density)
        self.lambda_er = lambda_er

    def calc_tension_dev_len(self):
        l_db = calc_l_db(self.bar_diameter, self.f_c, self.f_y)
        lambda_cf = calc_lambda_cf(self.bar_diameter, self.spacing, self.cover, self.epoxy_coat)
        lambda_rl = calc_lambda_rl(self.top_bar, self.f_c)
        lambda_rc = calc_lambda_rc(self.bar_diameter, self.c_b)
        self.l_d = max(l_db * min(lambda_rl * lambda_cf, 1.7) * lambda_rc * self.lambda_er / self.lambda_, 12)
        return self.l_d
    
    def calc_hook_dev_len(self, lambda_rc=1):
        l_hdb = calc_l_hdb(self.bar_diameter, self.f_c, self.f_y)
        lambda_cw = calc_lambda_cw(self.epoxy_coat)
        self.l_dh = l_hdb * (lambda_rc * lambda_cw * self.lambda_er / self.lambda_)
        return self.l_dh
    
    def calc_tension_lap_len(self, lap_class='B'):
        if lap_class == 'A':
            self.ten_lap_len = max(self.l_d, 12)
        else:
            self.ten_lap_len = max(1.3 * self.l_d, 12)
        return self.ten_lap_len

    def print_dev_lap(self):
        tension_development = return_ft_in(self.l_d / 12, multiple=1, direction='up')[1]
        tension_hook_development = return_ft_in(self.l_dh / 12, multiple=1, direction='up')[1]
        tension_splice = return_ft_in(self.ten_lap_len / 12, multiple=1, direction='up')[1]

        output = {
            'tension_development': tension_development,
            'tension_hook_development': tension_hook_development,
            'tension_splice': tension_splice
        }
        return output