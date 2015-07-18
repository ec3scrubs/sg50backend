from sqlite3 import dbapi2 as sqlite3

from flask import Flask, jsonify, request, g, abort, make_response
from flask_cors import CORS

DATABASE = ('test.db')
app = Flask(__name__)
cors = CORS(app)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None: db.close()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def add_student(name='test', age=10, sex='male'):
    sql = "INSERT INTO students (name, sex, age) VALUES('%s', '%s', %d)" % (
        name, sex, int(age))
    print sql
    db = get_db()
    db.execute(sql)
    res = db.commit()
    return res


def find_student(name=''):
    sql = "select * from students where name = '%s' limit 1" % (name)
    print sql
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    rv.close()
    if len(res) != 0:
        return res[0]
    else:
        abort(404)


def get_all_students():
    sql = "select * from students"
    print sql
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    rv.close
    print res
    return res


@app.route('/')
def users():
    result = get_all_students()
    ret_str = []
    for row in result:
        temp = []
        for object in row:
            temp.append(object)
        ret_str.append(temp)
    print str(ret_str)
    return str(ret_str)


@app.route('/add', methods=['POST'])
def add_user():
    if not request.json:
        abort(400)
    print add_student(name=request.json['name'], age=request.json['age'],
                      sex=request.jsongit['sex'])
    return ''


@app.route('/find_user/name/<string:name>', methods=['GET'])
def find_user_by_name(name):
    student = find_student(name)
    return jsonify(name=student['name'], age=student['age'], sex=student['sex'])


if __name__ == '__main__':
    app.run(debug=True)
