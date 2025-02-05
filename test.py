# from config import props_path
from dev_lap import ConcreteBeam, RebarDevLap
# from unit_conversion import return_ft_in
# from rebar import RebarProperties, RebarBend

bar_size = '#5'
spacing = 12
cover = 2
f_c = 4
f_y = 60
conc_density = 150

epoxy_coat = False
top_bar = False
lambda_er = 1

# hook dev len
lambda_rc = 1

lap_class = 'B'

# bar bend
stirrup = False
bar_bend = 90

beam = ConcreteBeam(bar_size, spacing, cover, f_c, f_y, conc_density)
rebar = RebarDevLap(beam, epoxy_coat, top_bar, lambda_er)
print(rebar.calc_tension_dev_len())
print(rebar.calc_hook_dev_len(lambda_rc))
print(rebar.calc_tension_lap_len(lap_class))
print(rebar.print_dev_lap())

# rebar.calc_tension_dev_len()
# out = return_ft_in(rebar.calc_tension_lap_len() / 12, multiple=1, direction='up')[1]
# print(out)

# rebar = RebarProperties(bar_size, props_path)
# bend = RebarBend(rebar, bar_bend)
# bend.set_bend_extension(stirrup)
# print(bend.calc_bend_dimension())