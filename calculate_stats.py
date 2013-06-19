import json
from collections import defaultdict
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('AGG')
import matplotlib.pyplot as plt

example_stations_by_time = defaultdict(dict)
def pandas_process_file(
        fname, field_name="availableDocks", 
        collection_dict=example_stations_by_time):
    stats = json.loads(open(fname).read())
    et = stats['executionTime']
    for s in stats['stationBeanList']:
        collection_dict[s['id']][et] = s[field_name]
    return stats


        
def process_directory(d_name):
    """This function processes all files in a directory that start with stations- and
    returns a dict of dicts suitable for pandas DataFrame ingestion"""
    stations_by_time = defaultdict(dict)
    #import pdb
    #pdb.set_trace()
    disregard, disregard2, station_files = os.walk(d_name).next()

    for fname in station_files:
        if fname.find('stations-') == -1:
            continue
        full_fname = os.path.join(d_name, fname)
        
        #print full_fname,
        try:
            pandas_process_file(full_fname, collection_dict=stations_by_time)
        except Exception, e:
            print e, full_fname
        

    return stations_by_time


def process_raw_files():
    # this is the most expedient way to setup the dataframe properly,
    # it's a bit of a hack

    
    df = pd.DataFrame(process_directory(os.path.expanduser('~/data_citibike')))
    df.to_csv('full_data.csv')
    df3 = pd.read_csv('full_data.csv', index_col=0, parse_dates=[0])
    return df3

def grab_existing():
    print "start grab_existing", dt.datetime.now()
    df3 = pd.read_csv('full_data.csv', index_col=0, parse_dates=[0])
    return df3

def process_dataframe(input_df):
    print "start process_dataframe", dt.datetime.now()
    # we need to sort the dataframe so that rows are arranged chronologically
    df = input_df.sort() 
    print "after sort", dt.datetime.now()
    # diff_df is the change in station occupancy from time period to time period
    diff_df = df.diff()
    print "after diff", dt.datetime.now()
    starting_trips = diff_df.where(diff_df < 0).fillna(0)
    starting_summaries = starting_trips.sum(axis=1)
    ending_trips = diff_df.where(diff_df > 0).fillna(0)
    ending_summaries = ending_trips.sum(axis=1)

    print "after trips_calcs", dt.datetime.now()
    return StationSummaries(df, diff_df, starting_trips, ending_trips)


import datetime as dt
one_hour = dt.timedelta(0,1)
one_day = dt.timedelta(1)
one_week = dt.timedelta(7)
all_time = dt.timedelta(70000)

class StationSummaries(object):
    def __init__(self, df, diff_df, starting_trips, ending_trips):
        self.df, self.diff_df = df, diff_df
        self.starting_trips, self.ending_trips =  starting_trips, ending_trips

    def produce_station_stats(self, station_id, now = False):
        if not now:
            now = dt.datetime.now()
        start_col = self.starting_trips[str(station_id)].abs()
        hour_df = start_col[now - one_hour:now]
        day_df = start_col[now - one_day:now]
        week_df = start_col[now-one_week:now]
        all_df = start_col[now-all_time:now]
        summary_stats = dict(
            starting = dict(
                hour=hour_df.sum(),
                day=day_df.sum(),
                week=week_df.sum(),
                all=all_df.sum()))
        return summary_stats

    def produce_station_plots(self, station_id, now = False):
        if not now:
            now = dt.datetime.now()
        start_col = self.starting_trips[str(station_id)]
        available_col = self.df[str(station_id)]
        
        hour_df = start_col[now - one_hour:now]
        day_df = start_col[now - one_day:now]
        week_df = start_col[now-one_week:now]
        all_df = start_col[now-all_time:now]


        a_hour_df = available_col[now - one_hour:now]
        a_day_df = available_col[now - one_day:now]
        a_week_df = available_col[now-one_week:now]
        a_all_df = available_col[now-all_time:now]
        
        directory = "site_root/plots/%s" % str(station_id)
        if not os.path.exists(directory):
            os.makedirs(directory)
        self.plot(hour_df, "site_root/plots/%s/hour.png" % str(station_id))
        self.plot(day_df, "site_root/plots/%s/day.png" % str(station_id))
        self.plot(week_df, "site_root/plots/%s/week.png" % str(station_id))
        self.plot(all_df, "site_root/plots/%s/all.png" % str(station_id))

        self.plot(a_hour_df, "site_root/plots/%s/avail_hour.png" % str(station_id))
        self.plot(a_day_df, "site_root/plots/%s/avail_day.png" % str(station_id))
        self.plot(a_week_df, "site_root/plots/%s/avail_week.png" % str(station_id))
        self.plot(a_all_df, "site_root/plots/%s/avail_all.png" % str(station_id))

        self.plot(hour_df.cumsum(), "site_root/plots/%s/hour_cumsum.png" % str(station_id))
        self.plot(day_df.cumsum(), "site_root/plots/%s/day_cumsum.png" % str(station_id))
        self.plot(week_df.cumsum(), "site_root/plots/%s/week_cumsum.png" % str(station_id))
        self.plot(all_df.cumsum(), "site_root/plots/%s/all_cumsum.png" % str(station_id))


    def produce_system_stats(self, now = False):

        if not now:
            now = dt.datetime.now()

        time_dict = dict(#hour=now - one_hour, 
                         day=now-one_day, week=now-one_week, all=now-all_time)
        stt = self.starting_trips[:now]
        base_starts = dict([[label, stt[time:]] for label, time in time_dict.items()])
        station_sums = dict([[label, base_starts[label].sum().abs()] for label, time in time_dict.items()])
        abs_station_sums = dict([[k, v.abs()] for k,v in station_sums.items()])
        [[k, v.sort(axis=1)] for k,v in abs_station_sums.items()]

        popular_starting_stations = dict(
            [[k, v.index.tolist()] for k,v in abs_station_sums.items()])
        [[k, v.reverse()] for k,v in  popular_starting_stations.items()]
        popular_starting_stations2 = dict(
                [[k, map(abs, map(int, v))] for k,v in  popular_starting_stations.items()])


        total_trips = dict(
            [[label, base_starts[label].sum().abs().sum()] for label, time in time_dict.items()])

        summary_stats =  dict(
            total_trips=total_trips,
            popular_starting_stations=popular_starting_stations2)


        return summary_stats


    def plot(self, df, fname):
        fig=plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(df.index,df)
        fig.autofmt_xdate()
        fig.savefig(fname)
        fig.clf()

if __name__ == "__main__":
    ss = process_dataframe(grab_existing())
    ss_dict = {}

    print "generating_station_summaries"
    print ss.produce_station_plots(363)

