from flask import Flask, request, jsonify
from flask_cors import CORS # needs to be installed in pythonanywhere
from config import num_keys, select_keys
from config import props_path
from rebar import RebarProperties, RebarBend
from dev_lap import ConcreteBeam, RebarDevLap

app = Flask(__name__)
CORS(app)

def extract_data(data, float_keys, str_keys):
    extracted_data = {}
    for key in float_keys:
        extracted_data[key] = float(data.get(key, 0))
    for key in str_keys:
        extracted_data[key] = data.get(key, '')
    return extracted_data

@app.route('/props', methods=['POST'])
def props():
    data = request.json
    bar_type = data.get('type')
    bar_size = data.get('size')
    bar_bend = data.get('bend')
    stirrup = bar_type == 'stirrup'

    rebar = RebarProperties(bar_size, props_path, stirrup)
    if bar_bend != 'None':
        bend = RebarBend(rebar, int(bar_bend))
        bend.set_bend_extension()
        bend_dimension = bend.calc_bend_dimension() if bar_bend else None
        add_length = bend.calc_add_length() if bar_bend else None
    else:
        bend_dimension = ''
        add_length = ''

    return jsonify({
        'bar_diameter': rebar.bar_diameter,
        'bar_area': rebar.bar_area,
        'bar_weight': rebar.bar_weight,
        'bar_perimeter': rebar.bar_perimeter,
        'pin_diameter': rebar.pin_diameter,
        'bend_dimension': bend_dimension,
        'add_length': add_length
    })

@app.route('/dev-lap', methods=['POST'])
def dev_lap():
    data = request.json
    values = extract_data(data, num_keys, select_keys)

    beam = ConcreteBeam(
        values['size'],
        values['spacing'],
        values['cover'],
        values['f_c'], 
        values['f_y'],
        values['concDensity']
        )

    # development and lap
    epoxy_coat = values['epoxy_coat'] != 'no'
    top_bar = values['top_bar'] != 'no'
    rebar = RebarDevLap(
        beam, 
        epoxy_coat, 
        top_bar, 
        values['lambda_er']
        )
    rebar.calc_tension_dev_len()
    rebar.calc_hook_dev_len()
    rebar.calc_tension_lap_len()
    output = rebar.print_dev_lap()

    return jsonify({
        'tension_development': output['tension_development'],
        'tension_hook_development': output['tension_hook_development'],
        'tension_splice': output['tension_splice']
    })

if __name__ == "__main__":
    app.run(debug=True)
