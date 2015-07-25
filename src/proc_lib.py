__author__ = 'mark'

import sqlite3 as lite

from geopy.distance import vincenty

home = (1.3725179, 103.83279)
feat_tmp = "school hospital"


def query_data(location, type, items=5):
    DATABASE = ('../data/data.db')
    type = type.lower()
    con = lite.connect(DATABASE)
    data = []
    res = []
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM data WHERE type='" + type + "';")
        data = cur.fetchall()

    tmp = []
    for row in data:
        c_loc = (row[2], row[3])
        tmp.append((row[0], vincenty(location, c_loc).km))
    tmp = sorted(tmp, key=lambda item: item[1])
    tmp = tmp[:items]
    res = tmp
    return res


def query_hdb(location, filter, items=5, low_price=300000, high_price=400000):
    DATABASE = ('../data/data.db')
    con = lite.connect(DATABASE)
    data = []
    res = []
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM hdb WHERE price>='"
                    + str(low_price) + "' AND price <= '" + str(
            high_price) + "';")
        data = cur.fetchall()
    tmp = []
    for row in data:
        c_loc = (row[2], row[3])
        distance = vincenty(location, c_loc).km
        new_item = Candidate(row, distance, filter)
        new_item.compute_swift()
        tmp.append(new_item)
    tmp = sorted(tmp)
    tmp = tmp[:items]
    res = tmp
    return res


class Candidate(object):
    def __init__(self, data, distance, filter):
        self.distance = distance
        self.price = data[7]
        self.address = data[1]
        self.location = (data[2], data[3])
        self.area = data[4]
        self.type = data[5]
        self.year = data[6]
        self.value = data[7] / float(data[4])
        self.filter = filter.split()
        self.score = 0
        self.features = {}

    def __lt__(self, other):
        if self.score != other.score:
            return self.score < other.score
        return self.price < other.price

    def compute_swift(self):
        price_factor = 1  # Tweak price factor to adjust the importance of
        # price, ironically higher number makes price less important
        price_calc = float(price_factor * 250)
        self.score = self.distance + self.value / price_calc

    def compute(self):
        for item in self.filter:
            self.features[item] = query_data(self.location, item)

    def display(self):
        print self.address, self.distance, int(self.value)


def query(location=home, features=feat_tmp):
    res = query_hdb(location, features)
    ret = {}
    ret["n_items"] = len(res)
    for item in res:
        item.compute()

    for (k, item) in enumerate(res):
        print k
        # ret[str(k)] = {}
        tmp = {}
        tmp["address"] = item.address
        tmp["distance"] = item.distance
        tmp["price"] = item.price
        tmp["score"] = item.score
        tmp["size"] = item.area
        tmp["value"] = item.value
        for elem in features.split():
            tmp[elem] = item.features[elem]
        ret[(str(k))] = tmp

    return ret


if __name__ == "__main__":
    # res = query_data(location=home,type="school")
    # app.run(debug=True)
    pass
