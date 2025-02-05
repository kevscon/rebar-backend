import os

# numerical input
num_keys = [
    'cover',
    'spacing',
    'f_c',
    'f_y',
    'concDensity',
    'lambda_er'
]
# selection input
select_keys = [
    'size',
    'epoxy_coat',
    'top_bar'
]

# rebar properties
local_props_path = '/data/props.csv'
# rebar grade
local_grade_path = '/data/grade.csv'

props_path = os.getcwd() + local_props_path
grade_path = os.getcwd() + local_grade_path