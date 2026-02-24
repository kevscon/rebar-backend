import pandas as pd
import math

def calc_arc_len(pin_diameter, bar_diameter, bar_bend):
    """
    Calculates the arc length of rebar at bend along centerline (in).

    Parameters:
    - pin_diameter: bend diameter of rebar (in).
    - bar_diameter: rebar diameter (in).
    - bar_bend: angle of bend (degrees).
    """
    return math.pi * (pin_diameter + bar_diameter) * bar_bend / 360

def calc_tangent_len(pin_diameter, bar_diameter):
    """
    Calculates the tangent length of rebar at bend (in).

    Parameters:
    - pin_diameter: bend diameter of rebar (in).
    - bar_diameter: rebar diameter (in).
    """
    return pin_diameter / 2 + bar_diameter

class RebarProperties:
    """
    Class to retrieve steel rebar properties.
    """
    def __init__(self, bar_size: str, data_path: str, stirrup=False):
        self.stirrup = stirrup
        self.bar_size = bar_size
        bar_props_df = pd.read_csv(data_path, dtype=str)
        prop_table = bar_props_df[bar_props_df['bar_size'] == bar_size]

        if prop_table.empty:
            raise ValueError(f"Bar size '{bar_size}' not found in the properties file.")

        self.properties = prop_table.iloc[0].to_dict()

    @property
    def bar_diameter(self):
        return float(self.properties['bar_diameter'])

    @property
    def bar_area(self):
        return float(self.properties['bar_area'])

    @property
    def bar_weight(self):
        return float(self.properties['bar_weight'])

    @property
    def bar_perimeter(self):
        return float(self.properties['bar_perimeter'])

    @property
    def pin_diameter(self):
        if self.stirrup == True:
            if self.bar_size in ['#3', '#4', '#5']:
                return 4 * self.bar_diameter
            elif self.bar_size in ['#6', '#7', '#8']:
                return 6 * self.bar_diameter
            else:
                raise ValueError(f"Not valid for pin diameter.")
        else:
            if self.bar_size in ['#3', '#4', '#5', '#6', '#7', '#8']:
                return 6 * self.bar_diameter
            elif self.bar_size in ['#9', '#10', '#11']:
                return 8 * self.bar_diameter
            elif self.bar_size in ['#14', '#18']:
                return 10 * self.bar_diameter
            else:
                raise ValueError(f"Not valid for pin diameter.")

class RebarBend:
    """
    Rebar subclass to calculate rebar bend dimensions.
    """
    def __init__(self, rebar_instance, bar_bend):
        self.stirrup = rebar_instance.stirrup
        self.bar_size = rebar_instance.bar_size
        self.bar_diameter = rebar_instance.bar_diameter
        self.pin_diameter = rebar_instance.pin_diameter
        self.bar_bend = bar_bend

    def set_bend_extension(self):
        if self.stirrup == False:
            if self.bar_bend == 90:
                self.bend_extension = 12 * self.bar_diameter
            elif self.bar_bend == 180:
                self.bend_extension = max(4 * self.bar_diameter, 2.5)
            else:
                raise ValueError(f"Bend '{self.bar_bend}' is not a valid hook.")
        else:
            if self.bar_bend == 90:
                if self.bar_size in ['#3', '#4', '#5']:
                    self.bend_extension = 6 * self.bar_diameter
                else:
                    self.bend_extension = 12 * self.bar_diameter
            elif self.bar_bend == 135:
                self.bend_extension = 6 * self.bar_diameter
            elif self.bar_bend == 180:
                self.bend_extension = max(4 * self.bar_diameter, 2.5)
            else:
                raise ValueError(f"Bend '{self.bar_bend}' is not a valid hook.")

    def calc_bend_dimension(self):
        self.bend_dimension = self.pin_diameter / 2 + self.bar_diameter + self.bend_extension
        return math.ceil(self.bend_dimension)
    
    def calc_add_length(self):
        arc_length = calc_arc_len(self.pin_diameter, self.bar_diameter, self.bar_bend)
        tangent_length = calc_tangent_len(self.pin_diameter, self.bar_diameter)
        self.add_length = self.bend_extension + arc_length + tangent_length
        return math.ceil(self.add_length)