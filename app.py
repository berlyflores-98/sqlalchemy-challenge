# Docs on session basics
# https://docs.sqlalchemy.org/en/13/orm/session_basics.html

import numpy as np
import os

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt
import pandas as pd

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
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
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/Start Date<br/>"
        f"/api/v1.0/Start/End Date<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of all Rainfall per Date"""

    # Query all Precipitation
    session = Session(engine)
    results = session.query(Measurement.date,Measurement.prcp).all()

    # close the session to end the communication with the database
    session.close()

    # Create a dictionary from the row data and append to a list of dates and rain
    all_prcp = []
    for prep in results:
        prep_dict = {(prep.date):prep.prcp}
        all_prcp.append(prep_dict)
    return jsonify(all_prcp)


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of Station data """

    # Open a communication session with the database
    session = Session(engine)

    # Query all station ids
    results = session.query(Station.station).all()

    # close the session to end the communication with the database
    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))
    print(all_stations)
    return jsonify(all_stations)



#Query the dates and temperature observations of the most active station for the last year of data.
#Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of temperature observations of the most active station for the last year of data """
    session = Session(engine)
    #getting the last data of the list
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Convert the data from string to datetime
    last_date_form = dt.datetime.strptime(last_date[0], '%Y-%m-%d').date()

    # Create a query data interval
    year_date = last_date_form - dt.timedelta(days=365)
    #getting the most active by temp
    temp_obv = session.query(Measurement.station,func.count(Measurement.tobs)).group_by(Measurement.station).order_by(func.count(Measurement.tobs).desc()).all()
    most_obv = temp_obv[0][0]
    #getting the last year of data from most active station
    temp_query = session.query(Measurement.date,Measurement.tobs).filter(Measurement.date > year_date,Measurement.station==most_obv).all()
    all_temp = list(np.ravel(temp_query))
    print(all_temp)
    return jsonify(all_temp)





if __name__ == '__main__':
    app.run(debug=True)
