from flask import Flask, json, request, jsonify, Response

import processing
import processing.triplets
import processing.rgb_blending

app = Flask(__name__)


@app.route('/api/generate_triplets', methods=['POST'])
def generate_triplets():
    """
    Returns the list of triplets.

    Test with:
    curl -X POST --header "Content-Type: application/json" --data '{"hello":"world"}' http://localhost:5000/api/generate_triplets

    For the moment data is not used.
    :return: The list of triplets.
    """
    body = json.loads(request.data)
    # Be careful the link is synchronous
    triplets = processing.triplets.generate_triplets()
    return json.jsonify(triplets)


@app.route('/api/rgb_blending', methods=['POST'])
def rgb_blending():
    """
    Compute the rbg blendings for all the triplets from the data body.

    Test with:
    curl -X POST --header "Content-Type: application/json" --data '[[1, 2, 3],[1.0, 3.3, 5],[1.0, 7, 15]]' http://localhost:5000/api/rbg_blending
    Be careful no to forget the trailing 0 when sending floats.

    For the moment data is not used.
    :return: "Done"
    """
    # data in string format and you have to parse into dictionary
    rgbs = json.loads(request.data)
    # Be careful the link is synchronous
    map(processing.rgb_blending.compute, rgbs)
    return "Done"


@app.errorhandler(Exception)
def handle_invalid_usage(error):
    response = jsonify({'msg': str(error)})
    response.status_code = 500
    return response


# from 3 to 80 with a step of 1, frequency is numpy.array's last dimension
# FIXME Maybe the max is only 39...
@app.route("/api/seismic_blend_png", methods=['GET'])
def render():
    """
    Returns the rbg blended slice as a png file.
    direction: a character ('x', 'y', 't') describing the direction perpendicular to the slice.
    index: index (integer) of the slice in the cube.
    f_r: index (integer) of the red frequency.
    f_g: index (integer) of the green frequency.
    f_b: index (integer) of the blue frequency.

    Test with:
    curl -X GET --header "Content-Type: application/json" "http://localhost:5000/api/seismic_blend_png?direction=x&index=50&f_r=5&f_g=6&f_b=20" --output some.png
    Be careful no to forget the trailing 0 when sending floats.

    :return: Raw png binary data or status code 500 with field "msg" if something went wrong.
    """
    direction = request.args.get("direction")
    if direction not in ('x', 'y', 't'):
        raise ValueError("direction '%s' is not in 'x', 'y', 't'" % direction)
    index = int(request.args.get("index"))
    f_r = int(request.args.get("f_r"))
    f_g = int(request.args.get("f_g"))
    f_b = int(request.args.get("f_b"))
    png_binary_data = processing.rgb_blending.seismic_blend_png(direction, index, (f_r, f_g, f_b))
    return Response(png_binary_data, mimetype='image/png')


@app.route("/api/rgb_log_png", methods=['GET'])
def rgb_log_png():
    """
    Returns the rbg log as a png file.
    f_r: index (integer) of the red frequency.
    f_g: index (integer) of the green frequency.
    f_b: index (integer) of the blue frequency.
    x (optional, default is 5): x coordinate index of the well.
    y (optional, default is 5): y coordinate index of the well.

    Test with:
    curl -X GET --header "Content-Type: application/json" "http://localhost:5000/api/rgb_log_png?f_r=5&f_g=6&f_b=20" --output some.png

    :return: Raw png binary data or status code 500 with field "msg" if something went wrong.
    """
    f_r = int(request.args.get("f_r"))
    f_g = int(request.args.get("f_g"))
    f_b = int(request.args.get("f_b"))
    x = int(request.args.get("x", 5))
    y = int(request.args.get("y", 5))
    png_binary_data = processing.rgb_blending.rgb_log_png(x, y, (f_r, f_g, f_b))
    return Response(png_binary_data, mimetype='image/png')


if __name__ == "__main__":
    app.run()
