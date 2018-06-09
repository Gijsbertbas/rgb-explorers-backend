from flask import Flask, json, request

import processing
import processing.triplets
import processing.rgb_blending

app = Flask(__name__)


@app.route('/generate_triplets', methods=['POST'])
def generate_triplets():
    """
    Returns the list of triplets.

    Test with:
    curl -X POST --header "Content-Type: application/json" --data '{"hello":"world"}' http://localhost:5000/generate_triplets

    For the moment data is not used.
    :return: The list of triplets.
    """
    body = json.loads(request.data)
    # Be careful the link is synchronous
    triplets = processing.triplets.generate_triplets()
    return json.jsonify(triplets)


@app.route('/rgb_blending', methods=['POST'])
def rgb_blending():
    """
    Compute the rbg blendings for all the triplets from the data body.

    Test with:
    curl -X POST --header "Content-Type: application/json" --data '[[1, 2, 3],[1.0, 3.3, 5],[1.0, 7, 15]]' http://localhost:5000/rbg_blending
    Be careful no to forget the trailing 0 when sending floats.

    For the moment data is not used.
    :return: "Done"
    """
    # data in string format and you have to parse into dictionary
    rgbs = json.loads(request.data)
    # Be careful the link is synchronous
    map(processing.rgb_blending.compute, rgbs)
    return "Done"


# from 3 to 80 with a step of 1, frequency is numpy.array's last dimension
# FIXME Maybe the max is only 39...
@app.route("/seismic_blend_png", methods=['GET'])
def render():
    """
    Test with:
    curl -X GET --header "Content-Type: application/json"  "http://localhost:5000/seismic_blend_png?direction=x&index=50&f_r=5&f_g=6&f_b=20"
    Be careful no to forget the trailing 0 when sending floats.
    :return:
    """
    direction = request.args.get("direction")
    if direction not in ('x', 'y', 't'):
        raise ValueError("direction '%s' is not in 'x', 'y', 't'" % direction)
    index = int(request.args.get("index"))
    f_r = int(request.args.get("f_r"))
    f_g = int(request.args.get("f_g"))
    f_b = int(request.args.get("f_b"))
    return processing.rgb_blending.seismic_blend_png(direction, index, (f_r, f_g, f_b))


@app.route("/rgb_log_png", methods=['GET'])
def rgb_log_png():
    """
    Test with:
    curl -X GET --header "Content-Type: application/json"  "http://localhost:5000/rgb_log_png?f_r=5&f_g=6&f_b=20"
    Be careful no to forget the trailing 0 when sending floats.
    :return:
    """
    f_r = int(request.args.get("f_r"))
    f_g = int(request.args.get("f_g"))
    f_b = int(request.args.get("f_b"))
    x, y = 5, 5
    return processing.rgb_blending.rgb_log_png(x, y, (f_r, f_g, f_b))


if __name__ == "__main__":
    app.run()
