# Import the dependencies.
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """Following are all available API routes."""
    return (
        f"Available API Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    last_row = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year_1 = dt.date(2017,8,23) - dt.timedelta(days= 365)

    prcp_score_year = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= year_1, Measurement.prcp != None).\
    order_by(Measurement.date).all()

    dates_prcp = []
    
    for prcpdate in prcp_score_year:
        prcpdate_dict = {}
        prcpdate_dict["date"] = prcpdate.date
        prcpdate_dict["prcp"] = prcpdate.prcp
        dates_prcp.append(prcpdate_dict)

    return jsonify(dict(prcp_score_year))

@app.route("/api/v1.0/stations")
def stations():
    session.query(Measurement.station).distinct().count()
    active_stations = session.query(Measurement.station,func.count(Measurement.station)).\
                               group_by(Measurement.station).\
                               order_by(func.count(Measurement.station).desc()).all()
    
    act_sta = []
    for station_dict in active_stations:
        sta_dict = {}
        sta_dict["station"] = station_dict.station
        act_sta.append(sta_dict)

    return jsonify(dict(active_stations))


@app.route("/api/v1.0/tobs")
def tobs():
    
    year_1 = dt.date(2017,8,23) - dt.timedelta(days= 365)
    year_temperature = session.query(Measurement.tobs).\
        filter(Measurement.date >= year_1, Measurement.station == 'USC00519281').\
         order_by(Measurement.tobs).all()

    year_temp = []
    for y_temp in year_temperature:
        yrtemp = {}
        yrtemp["tobs"] = y_temp.tobs
        year_temp.append(yrtemp)

    return jsonify(year_temp)


def calc_start_temps(start_date):
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

@app.route("/api/v1.0/<start>")
    
def start_date(start):
    calc_start_temp = calc_start_temps(start)
    t_temp= list(np.ravel(calc_start_temp))

    t_min = t_temp[0]
    t_max = t_temp[2]
    t_avg = t_temp[1]
    t_dictionary = {'Minimum temperature': t_min, 'Maximum temperature': t_max, 'Avg temperature': t_avg}

    return jsonify(t_dictionary)

def calc_temps(start_date, end_date):
    return session.query(func.min(Measurement.tobs), \
                         func.avg(Measurement.tobs), \
                         func.max(Measurement.tobs)).\
                         filter(Measurement.date >= start_date).\
                         filter(Measurement.date <= end_date).all()


@app.route("/api/v1.0/<start>/<end>")

def start_end_date(start, end):
    
    calc_temp = calc_temps(start, end)
    ta_temp= list(np.ravel(calc_temp))

    tmin = ta_temp[0]
    tmax = ta_temp[2]
    temp_avg = ta_temp[1]
    temp_dictionary = { 'Minimum temperature': tmin, 'Maximum temperature': tmax, 'Avg temperature': temp_avg}

    return jsonify(temp_dictionary)
    

if __name__ == '__main__':
    app.run(debug=True)