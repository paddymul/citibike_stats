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

def write_html(s, ss):
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('station.html')

    s.update(ss.produce_station_plots(s['id'], 'foo', dt.datetime(2013,6,13)))

    output_from_parsed_template = template.render(s=s)
    # to save the results
    with open("station_html/s%d.html" % s['id'], "wb") as fh:
        fh.write(output_from_parsed_template)
#
# In [4]: stations_by_id[528]
# Out[4]: 
# {u'altitude': u'',
#  u'availableBikes': 11,
#  u'availableDocks': 27,
#  u'city': u'',
#  u'id': 528,
#  u'landMark': u'',
#  u'lastCommunicationTime': None,
#  u'latitude': 40.74290902,
#  u'location': u'',
#  u'longitude': -73.97706058,
#  u'postalCode': u'',
#  u'stAddress1': u'2 Av & E 30 St',
#  u'stAddress2': u'',
#  u'stationName': u'2 Av & E 30 St',
#  u'statusKey': 1,
#  u'statusValue': u'In Service',
#  u'testStation': False,
# u'totalDocks': 39}




def produce_single_summary(k, v, ss):

    s1 = stations_by_id[v['closest_stations'][1]]
    print k, s1['id'], s1['stAddress1'], v['station_distances'][v['closest_stations'][1]]
    s2 = stations_by_id[v['closest_stations'][2]]
    print k, s2['id'], s2['stAddress1'], v['station_distances'][v['closest_stations'][2]]
    s3 = stations_by_id[v['closest_stations'][3]]
    print k, s3['id'], s3['stAddress1'], v['station_distances'][v['closest_stations'][3]]
    write_html(v, ss)

def produce_all_summaries():
    for k,v in stations_by_id.items():
        print "\n\n"
        print "="*80

        if k == 146:
            continue
        try:
            produce_single_summary(k,v,ss)
        except Exception, e:
            print "ERROR with k", k
            print e

stations_by_id = write_data_file()
ss = calculate_stats.process_dataframe(calculate_stats.grab_existing())
if __name__ == "__main__":
    #produce_single_summary(448, stations_by_id[448], ss)
    start_dt = dt.datetime.now()
    print "START DT", start_dt
    produce_all_summaries()
    end_dt = dt.datetime.now()
    print "END_DT", end_dt, end_dt - start_dt

