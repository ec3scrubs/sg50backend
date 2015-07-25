import json
import urllib2

from flask import Flask, jsonify, make_response, request, abort
from flask_cors import CORS

import proc_lib

app = Flask(__name__)
cors = CORS(app)


def callSD(query):
    query = query.replace(' ', '%20')
    latlong = []
    data = json.load(urllib2.urlopen(
        "http://www.streetdirectory.com/api/?mode=search&act=all&profile=sd_mobile&country=sg&q=" + str(
            query) + "&output=json&start=0&limit=1"))
    print data
    if len(data) > 1:
        lat = data[1]['y']
        lng = data[1]['x']
    else:
        lat = data[0]['y']
        lng = data[0]['x']
    return (lat, lng)


# Posting search query to backend
@app.route('/api/query', methods=['POST'])
def create_entry():
    # fetch latlong from SD based on address
    # call backend to fetch results

    if not request.json or not 'address' in request.json:
        abort(400)
    latlong = callSD(str(request.json.get('address')))
    feat = request.json.get("features")
    print feat
    # backend processes based on the latlong

    # housing.append(latlong)
    return jsonify(proc_lib.query(location=latlong, features=feat)), 201


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    app.run(debug=True)
