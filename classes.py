import pandas as pd
import math, os

class OtherRebarProperties:

    def __init__(self, bar_size):
        self.bar_size = bar_size
        self.bar_props_df = pd.read_csv(os.getcwd() + '/eng_apps/apps/rebar/data/props.csv', dtype=str)
        self.bar_bends_df = pd.read_csv(os.getcwd() + '/eng_apps/apps/rebar/data/bends_other.csv', dtype=str)
        self.prop_table = self.bar_props_df[self.bar_props_df['bar_size'] == self.bar_size]

    def return_bar_properties(self):
        self.bar_diameter = float(self.prop_table['bar_diameter'].values[0])

        props_dict = {
            'Bar Diameter (in)': str(self.bar_diameter),
            'Bar Area (in²)': self.prop_table['bar_area'].values[0],
            'Bar Weight (plf)': self.prop_table['bar_weight'].values[0],
            'Bar Perimeter (in)': self.prop_table['bar_perimeter'].values[0],
        }
        return props_dict


    def return_bend_dims(self, bar_bend):

        bend_table = self.bar_bends_df[
            (self.bar_bends_df['bar_size'] == self.bar_size) &
            (self.bar_bends_df['bar_bend'] == bar_bend)
        ]

        pin_diameter = bend_table['D'].values[0]
        # calculate B dimension
        if bar_bend == '180':
            B = max(4 * self.bar_diameter + 0.5 * float(pin_diameter) + self.bar_diameter, 2.5)
        elif bar_bend == '135':
            B = max(6 * self.bar_diameter + 0.5 * float(pin_diameter) + self.bar_diameter, 2.5)
        else:
            B = '-'

        bend_dict = {
            'D': pin_diameter,
            'A': bend_table['A'].values[0],
            'B': B,
            'C': bend_table['C'].values[0]
        }

        return bend_dict


class MainRebarProperties:

    def __init__(self, bar_size, bar_spacing, bar_bundle):
        self.bar_size = bar_size
        self.bar_spacing = float(bar_spacing)
        self.bar_bundle = int(bar_bundle)
        self.bar_props_df = pd.read_csv(os.getcwd() + '/eng_apps/apps/rebar/data/props.csv', dtype=str)
        self.bar_bends_df = pd.read_csv(os.getcwd() + '/eng_apps/apps/rebar/data/bends_main.csv', dtype=str)

        self.prop_table = self.bar_props_df[self.bar_props_df['bar_size'] == self.bar_size]
        self.bar_diameter = float(self.prop_table['bar_diameter'].values[0])
        self.bar_area = float(self.prop_table['bar_area'].values[0])
        self.steel_area = round(self.bar_area * self.bar_bundle * 12 / self.bar_spacing, 2)


    def in_to_ft_in(self, in_inches):
        feet = int(in_inches / 12)
        inches = in_inches % 12
        return str(feet) + "'-" + str(inches) + '"'


    def return_bar_properties(self):
        props_dict = {
            'Bar Diameter (in)': str(self.bar_diameter),
            'Bar Area (in²)': str(self.bar_area),
            'Bar Weight (plf)': self.prop_table['bar_weight'].values[0],
            'Bar Perimeter (in)': self.prop_table['bar_perimeter'].values[0],
            'As (in²/ft)': self.steel_area
        }

        return props_dict


    def return_bend_dims(self, bar_bend):
        if bar_bend == 'straight':
            bend_dict = {
                'D': '-',
                'A': '-',
                'B': '-',
                'C': '-'
            }

        else:
            bend_table = self.bar_bends_df[
                (self.bar_bends_df['bar_size'] == self.bar_size) &
                (self.bar_bends_df['bar_bend'] == bar_bend)
            ]

            pin_diameter = bend_table['D'].values[0]
            # calculate B dimension
            if bar_bend == '180':
                B = max(4 * self.bar_diameter + 0.5 * float(pin_diameter) + self.bar_diameter, 2.5)
            else:
                B = '-'

            bend_dict = {
                'D': pin_diameter,
                'A': bend_table['A'].values[0],
                'B': B,
                'C': bend_table['C'].values[0]
            }

        return bend_dict


    def return_tension_lengths(self, f_c, fy, bar_cover, bar_loc, coating,
                               lap_class, concrete_type, concrete_density, As_req):
        # development
        l_db = 2.4 * self.bar_diameter * (fy / math.sqrt(f_c))

        if concrete_type == 'normal':
            lambda_ = 1
        else:
            lambda_ = min(max(7.5 * float(concrete_density) / 1000, 0.75), 1)

        if bar_loc == 'top':
            lambda_rl = 1.3
        else:
            lambda_rl = 1

        if coating == 'none':
            lambda_cf = 1
        else:
            clear_spacing = self.bar_spacing - self.bar_diameter
            if bar_cover < 3 * self.bar_diameter or clear_spacing < 6 * self.bar_diameter:
                lambda_cf = 1.5
            else:
                lambda_cf = 1.2

        c_b = min(0.5 * self.bar_diameter + bar_cover, 0.5 * self.bar_spacing)
        lambda_rc = min(max(self.bar_diameter / c_b, 0.4), 1)

        if As_req:
            lambda_er = As_req / self.steel_area
        else:
            lambda_er = 1

        if lambda_rl * lambda_cf <= 1.7:
            l_d = max(l_db*lambda_rl*lambda_cf*lambda_rc*lambda_er/lambda_, 12)
        else:
            l_d = max(l_db*1.7*lambda_rc*lambda_er/lambda_, 12)

        # lap
        if lap_class == 'A':
            l_t = max(l_d, 12)
        else:
            l_t = max(1.3 * l_d, 12)

        if self.bar_bundle == 4:
            l_t = 1.33 * l_t
        elif self.bar_bundle == 3:
            l_t = 1.2 * l_t

        return {'Development Length': self.in_to_ft_in(math.ceil(l_d)), 'Lap Splice Length': self.in_to_ft_in(math.ceil(l_t))}


    def return_hook_length(self, f_c, fy, coating, concrete_type, concrete_density, lambda_rc, As_req):
        # development
        l_hb = (38 * self.bar_diameter) / 60 * fy / math.sqrt(f_c)

        if concrete_type == 'normal':
            lambda_ = 1
        else:
            lambda_ = min(max(7.5 * float(concrete_density) / 1000, 0.75), 1)

        if coating == 'none':
            lambda_cw = 1
        else:
            lambda_cw = 1.2

        if As_req:
            lambda_er = As_req / self.steel_area
        else:
            lambda_er = 1

        l_dh = max(l_hb*lambda_rc*lambda_cw*lambda_er/lambda_, 8 * self.bar_diameter, 6)

        return {'Development Length': self.in_to_ft_in(math.ceil(l_dh))}


    def return_compression_lengths(self, f_c, fy, lambda_rc, m, As_req):
        # development
        l_db = max((0.63 * self.bar_diameter * fy) / math.sqrt(f_c), 0.3 * self.bar_diameter * fy)

        if As_req:
            lambda_er = As_req / self.steel_area
        else:
            lambda_er = 1

        l_d = max(l_db*lambda_er*lambda_rc, 8)

        # lap
        if fy <= 60:
            l_c = max(0.5 * m * fy * self.bar_diameter, 12)
        else:
            l_c = max(m * (0.9 * fy - 24) * self.bar_diameter, 12)

        if self.bar_bundle == 4:
            l_c = 1.33 * l_c
        elif self.bar_bundle == 3:
            l_c = 1.2 * l_c

        return {'Development Length': self.in_to_ft_in(math.ceil(l_d)), 'Lap Splice Length': self.in_to_ft_in(math.ceil(l_c))}
