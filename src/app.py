import json
import urllib2

from flask import Flask, jsonify, json, make_response, request, abort
from flask_cors import CORS

import proc_lib

app = Flask(__name__)
cors = CORS(app)


def callSD(query):
    query = query.replace(' ', '%20')
    print "QUERY: " + query
    latlong = []
    data = json.load(urllib2.urlopen(
        "http://www.streetdirectory.com/api/?mode=search&act=all&profile=sd_mobile&country=sg&q=" + str(
            query) + "&output=json&start=0&limit=1"))
    # print data
    try:
        if len(data) > 1:
            lat = data[1]['y']
            lng = data[1]['x']
        else:
            lat = data[0]['y']
            lng = data[0]['x']
        return (lat, lng)
    except:
        abort(400)


# Posting search query to backend
@app.route('/api/query', methods=['POST'])
def create_entry():
    # fetch latlong from SD based on address
    # call backend to fetch results

    if not request.json or not 'address' in request.json:
        abort(400)
    latlong = callSD(str(request.json.get('address')))
    feat = request.json.get("features")
    minprice = request.json.get("minprice")
    maxprice = request.json.get("maxprice")
    # 'Child Care', 'Clinic', 'Community Club', 'Disabled-Friendly',
    # 'Elder Care', 'Exercise Facilities', 'Family', 'Hawker Centre',
    #  'Hospital', 'Kindergarten', 'Library', 'Nursing', 'Play',
    #  'Relaxation', 'School'
    # cdcouncil, childcare, clinic, comclub, disabled, eldercare, exercise,
    # family, hawker, heritage, hospital, kindergarten, lib (library),
    #  monument, museum, nursing, play, relax, school

    feat_map = {"Child Care": "childcare", "Community Club": "comclub",
                "Clinic": "clinic", "Disabled-Friendly": "disabled",
                "Elder Care": "eldercare", "Exercise Facilities": "exercise",
                "Family": "family", "Hawker Centre": "hawker",
                "Kindergarten": "kindergarten", "Library": "lib",
                "Nursing": "nursing", "Play": "play", "Relaxation": "relax",
                "School": "school"}
    # backend processes based on the latlong
    feat_send = ""
    for k in feat:
        feat_send += feat_map[k] + " "

    if feat_send is "":
        feat_send = "school clinic"

    # housing.append(latlong)
    return json.dumps(proc_lib.query(
        location=latlong,
        features=feat_send,
        minprice=int(minprice) * 1000,
        maxprice=int(maxprice) * 1000
    )), 201
    # return jsonify(proc_lib.query()), 201


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    app.run(debug=True)
