from flask import Flask, jsonify, make_response, request, abort
import json
import urllib2

import proc_lib

app = Flask(__name__)

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]

housing = [
    {
        'id': 1,
        'region': 'Serangoon',
        'address': '507 Serangoon North Avenue 4',
        'postal': '550507',
        'price': '300000',
        'x': '103.875386',
        'y': '1.371973',
        'nearby': {
            
        }
    }
]

def callSD(query):
    query = query.replace(' ', '%20')
    latlong = []
    data = json.load(urllib2.urlopen("http://www.streetdirectory.com/api/?mode=search&act=all&profile=sd_mobile&country=sg&q="+ str(query) +"&output=json&start=0&limit=1"))
    print data
    if len(data) > 1:
        lat = data[1]['y']
        lng = data[1]['x']
    else:
        lat = data[0]['y']
        lng = data[0]['x']
    latlong.append(lat)
    latlong.append(lng)
    return latlong

@app.route('/api/testfunc', methods=['GET'])
def get_tasks():
    return jsonify({'locations': housing})


@app.route('/api/testfunc/id/<int:loc_id>', methods=['GET'])
def get_task(loc_id):
    loc = [loc for loc in housing if loc['id'] == loc_id]
    if len(loc) == 0:
        abort(404)
    return jsonify({'locations': loc[0]})

#Posting search query to backend
@app.route('/api/query', methods=['POST'])
def create_entry():
    #fetch latlong from SD based on address
    #call backend to fetch results

    # if not request.json or not 'address' in request.json:
    #     abort(400)
    # latlong = callSD(str(request.json.get('address')))
    #backend processes based on the latlong
    return jsonify(proc_lib.test()), 201
    #return jsonify({'newEntry': latlong}), 201

def test_entry():
    latlong = callSD(str(request.json.get('address')))


@app.route('/api/testfunc/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'title' in request.json and type(request.json['title']) != unicode:
        abort(400)
    if 'description' in request.json and type(request.json['description']) is not unicode:
        abort(400)
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)
    task[0]['title'] = request.json.get('title', task[0]['title'])
    task[0]['description'] = request.json.get('description', task[0]['description'])
    task[0]['done'] = request.json.get('done', task[0]['done'])
    return jsonify({'task': task[0]})

@app.route('/api/testfunc/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    tasks.remove(task[0])
    return jsonify({'result': True})

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    app.run(debug=True)
