import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Meas = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Vacation API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2016-08-27<br/>"
        f"/api/v1.0/2016-08-27/2016-09-10<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    results = session.query(Meas.date, Meas.prcp).all()

    session.close()

    all_dates = []
    for date, prcp in results:
        dates_dict = {}
        dates_dict["date"] = date
        dates_dict["percipitation"] = prcp
        all_dates.append(dates_dict)

    return jsonify(all_dates)

@app.route("/api/v1.0/stations")
def stations():
     # Create our session (link) from Python to the DB
    session = Session(engine)

    results = session.query(Meas.station).\
        group_by(Meas.station).all()

    session.close()

    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Query the dates and temperature observations of the most active station for the last year of data.
    # Return a JSON list of temperature observations (TOBS) for the previous year.
    session = Session(engine)
    #Get last date of the data and calculate the date from one year previously.
    last_date = dt.datetime.strptime((session.query(Meas.date).order_by(Meas.date.desc()).first())[0],'%Y-%m-%d')
    target_date = dt.date((last_date).year-1, (last_date).month, (last_date).day)

    #Determine most active station for the last year of data.
    sel = [Meas.station, func.count(Meas.date)]
    station_data = session.query(*sel).\
        filter(Meas.date >= target_date).\
        group_by(Meas.station).\
        order_by(func.count(Meas.date).desc()).all()
    station_max_id = station_data[0][0]

    #Create query based on results
    sel = [Meas.date, Meas.tobs]
    tobs_data = session.query(*sel).\
        filter(Meas.station == station_max_id).\
        filter(Meas.date >= target_date).\
        order_by(Meas.date).all()

    session.close()

    tobs_year = []
    for date, tobs in tobs_data:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["temperature"] = tobs
        tobs_year.append(tobs_dict)

    print(f"Total entries for station {station_max_id} for the period past {target_date} is {len(tobs_year)}.")
    return jsonify(tobs_year)



@app.route("/api/v1.0/<start>")
def start_date(start):
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.

    session = Session(engine)
    sel = [func.min(Meas.tobs), func.max(Meas.tobs), func.avg(Meas.tobs)]
    temp_stats = session.query(*sel).\
        filter(Meas.date >= start).all()

    session.close()

    tobs_start = []
    for minimum, maximum, avg in temp_stats:
        tobs_dict = {}
        tobs_dict["minimum Temp"] = minimum
        tobs_dict["maximum Temp"] = maximum
        tobs_dict["average Temp"] = round(avg,1)
        tobs_start.append(tobs_dict)

    return jsonify(tobs_start)


@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
    session = Session(engine)
    sel = [func.min(Meas.tobs), func.max(Meas.tobs), func.avg(Meas.tobs)]
    temp_stats = session.query(*sel).\
        filter(Meas.date >= start).\
        filter(Meas.date <= end).all()

    session.close()

    tobs_start_end = []
    for minimum, maximum, avg in temp_stats:
        tobs_dict = {}
        tobs_dict["minimum Temp"] = minimum
        tobs_dict["maximum Temp"] = maximum
        tobs_dict["average Temp"] = round(avg,1)
        tobs_start_end.append(tobs_dict)

    return jsonify(tobs_start_end)

if __name__ == "__main__":
    app.run(debug=True)