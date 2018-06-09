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


if __name__ == "__main__":
    app.run()
