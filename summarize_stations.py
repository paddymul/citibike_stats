from collections import defaultdict
import json
example_stations_by_time = defaultdict(dict)
def pandas_process_file(fname, field_name="availableDocks", collection_dict=example_stations_by_time):
    stats = json.loads(open(fname).read())
    et = stats['executionTime']
    for s in stats['stationBeanList']:
        collection_dict[s['id']][et] = s[field_name]
    return stats

def write_data_file():
    ab = pandas_process_file('stations-05-28-16_04_24.json')
    station_data = ab['stationBeanList']
    stations_by_id = {}
    for s in station_data:
        stations_by_id[s['id']] = s
    open('station_data.json', "w").write(json.dumps(stations_by_id))
    for k,v in stations_by_id.items():
        dmap = construct_station_dist_map(stations_by_id, v)
        v['closest_stations'] = dmap.keys()
        v['station_distances'] = dict(dmap.items())
        
    return stations_by_id



from collections import OrderedDict
def construct_station_dist_map(by_id, s):
    dist_map = {}
    for k, s2 in by_id.iteritems():
        dist_map[k] = station_distance(s, s2)
    return OrderedDict(sorted(dist_map.items(), key=lambda t: t[1]))

def station_distance(s1, s2):
    return distance(
        s1['latitude'], s1['longitude'],
        s2['latitude'], s2['longitude'])

import math
 
def distance(lat1, lon1, lat2, lon2):
    radius = 6371 # km
 
    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c
    return d

from jinja2 import Environment, FileSystemLoader
import calculate_stats
import datetime as dt

complete_summaries = {}

# {'all_time_starting_trips': 295.0,
#  u'altitude': u'',
#  u'availableBikes': 21,
#  u'availableDocks': 14,
#  u'city': u'',
#  'closest_stations': [72,
#   480,
#   508,
#   495,],
#  'day_starting_trips': 68.0,
#  'hour_starting_trips': 0,
#  u'id': 72,
#  u'landMark': u'',
#  u'lastCommunicationTime': None,
#  u'latitude': 40.76727216,
#  u'location': u'',
#  u'longitude': -73.99392888,
#  u'postalCode': u'',
#  u'stAddress1': u'W 52 St & 11 Av',
#  u'stAddress2': u'',
#  u'stationName': u'W 52 St & 11 Av',
#  'station_distances': {72: 0.0,
#   79: 5.461241129523938,
#   82: 6.259903786989711,
#   83: 9.396643395659359,
#   116: 2.905835095023139,
#   119: 8.02767027885375,
#   120: 9.415747374933149},
#  u'statusKey': 1,
#  u'statusValue': u'In Service',
#  u'testStation': False,
#  u'totalDocks': 39,
#  'week_starting_trips': 295.0}




def write_station_html(s):
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('station.html')

    output_from_parsed_template = template.render(s=s, sbid=stations_by_id)
    # to save the results
    with open("station_html/s%d.html" % s['id'], "wb") as fh:
        fh.write(output_from_parsed_template)

def write_system_html(s):
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('index.html')

    output_from_parsed_template = template.render(s=s, sbid=stations_by_id)
    # to save the results
    with open("station_html/index.html", "wb") as fh:
        fh.write(output_from_parsed_template.encode('utf-8'))


def produce_single_summary(v):
    v.update(ss.produce_station_stats(v['id']))
    #ss.produce_station_plots(v['id'])  #, dt.datetime(2013,6,13)))
    complete_summaries[v['id']] = v
    v['fname']= v['stAddress1'].replace(" ", "_").replace("&", "and")
    write_station_html(v)

def produce_all_summaries():

    for k,v in stations_by_id.items():
     
        if k == 146:
            continue
        try:
            print k,v['stAddress1']
            produce_single_summary(v)
        except Exception, e:
            print "ERROR with k", k
            print e

stations_by_id = write_data_file()
ss = calculate_stats.process_dataframe(calculate_stats.grab_existing())
s_stats = ss.produce_system_stats()
if __name__ == "__main__":
    #produce_single_summary(448, stations_by_id[448], ss)
    start_dt = dt.datetime.now()
    print "START DT", start_dt
    write_system_html(s_stats)
    produce_all_summaries()
    end_dt = dt.datetime.now()
    print "END_DT", end_dt, end_dt - start_dt

