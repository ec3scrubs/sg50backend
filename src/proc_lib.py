__author__ = 'mark'

import sqlite3 as lite
from geopy.distance import vincenty

home = (1.3725179, 103.83279)

def query_data(location,type):
    DATABASE = ('../data/data.db')
    type = type.lower()
    con = lite.connect(DATABASE)
    data = []
    res = []
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM data WHERE type='"+type+"';")
        data = cur.fetchall()

    tmp = []
    for row in data:
        c_loc = (row[2], row[3])
        tmp.append((row[0],vincenty(location, c_loc).km))
    tmp = sorted(tmp, key=lambda item:item[1])
    tmp = tmp[:10]
    res = tmp
    return res


if __name__ == "__main__":
    res = query_data(location=home,type="school")
    for (x,y) in res:
        print x, y
