__author__ = 'mark'

import sqlite3 as lite

def query_sql(type):
    DATABASE = ('../data/data.db')
    type = type.lower()
    con = lite.connect(DATABASE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM data WHERE type='"+type+"';")
        res = cur.fetchall()
        print res


if __name__ == "__main__":
    query_sql(type="school")