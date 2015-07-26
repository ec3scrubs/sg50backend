__author__ = 'mark'

import sqlite3 as lite

from geopy.distance import vincenty

home = (1.3725179, 103.83279)
feat_tmp = "school hospital"
health_min = 1/31.1581329269627
health_max = 1/2.41345423511789
health_denom = health_max - health_min
elder_min = 1/26.9682768130885
elder_max = 1/4.56483642773025
elder_denom = elder_max - elder_min
family_min = 1/21.3751786450861
family_max = 1/3.31806535263963
family_denom = family_max - family_min

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
    tmp = [{"name":x,"dist":y} for (x,y) in tmp]
    res = tmp
    return res


def query_hdb(location, filter, items=5, low_price=300000, high_price=400000):
    DATABASE = ('../data/data.db')
    print low_price, high_price
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
        self.healthscore = ((1/data[8]) - health_min) / health_denom
        self.elderscore = ((1/data[9]) - elder_min) / elder_denom
        self.familyscore = ((1/data[10]) - family_min) / family_denom
        self.features = {}

    def __lt__(self, other):
        if self.score != other.score:
            return self.score > other.score
        return self.price < other.price

    def compute_swift(self):
        price_factor = 1  # Tweak price factor to adjust the importance of
        # price, ironically higher number makes price less important
        price_calc = float(price_factor * 6000)
        dist = 0
        try:
            dist = 1/self.distance
        except:
            dist = 0

        if dist > 1.5:
            dist = 1.5
        self.score = dist + (1/self.value)*price_calc
        other_score = (self.healthscore + self.elderscore +
                       self.familyscore)/2.5
        if self.score > 2:
            print self.score,self.distance, dist, (1/self.value)*price_calc, \
                other_score
        self.score += other_score

    def compute(self):
        for item in self.filter:
            self.features[item] = query_data(self.location, item)

    def display(self):
        print self.address, self.distance, int(self.value)


def query(location=home, features=feat_tmp, minprice=200000, maxprice=400000):
    res = query_hdb(location, features, low_price=minprice, high_price=maxprice)
    ret = []
    # ret = {}
    # ret["n_items"] = len(res)
    for item in res:
        item.compute()

    feat_map = {"Child Care": "childcare", "Community Club": "comclub",
                "Clinic": "clinic", "Disabled-Friendly": "disabled",
                "Elder Care": "eldercare", "Exercise Facilities": "exercise",
                "Family": "family", "Hawker Centre": "hawker",
                "Kindergarten": "kindergarten", "Library": "lib",
                "Nursing": "nursing", "Play": "play", "Relaxation": "relax",
                "School": "school", "Hospital": "hospital"}
    feat_map = {v:k for (k,v) in feat_map.iteritems()}

    for (k, item) in enumerate(res):
        # ret[str(k)] = {}
        tmp = {}
        tmp["address"] = item.address
        tmp["distance"] = item.distance
        tmp["price"] = item.price
        tmp["size"] = item.area
        tmp["value"] = item.value
        tmp["healthscore"] = item.healthscore * 100
        tmp["elderscore"] = item.elderscore * 100
        tmp["familyscore"] = item.familyscore * 100
        tmp["score"] = item.score * 20
        tmp["features"] = {}
        for elem in features.split():
            tmp["features"][feat_map[elem]] = item.features[elem]
        # ret[(str(k))] = tmp
        ret.append(tmp)
    return ret


if __name__ == "__main__":
    # res = query_data(location=home,type="school")
    # app.run(debug=True)
    pass
