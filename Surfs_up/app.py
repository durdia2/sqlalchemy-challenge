# Import the dependencies.
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
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station= Base.classes.station
# Create our session (link) from Python to the DB

session = Session(bind=engine)

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
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all precipitation and dates"""
    # Query all precipitation and date

    results = session.query(Measurement.date,Measurement.prcp).all()

    session.close()

    # Convert list of tuples into dictionary
    all_precipitation=[]
    for date,prcp in results:
        precipitation_dict = {}
        precipitation_dict[date] = prcp
        all_precipitation.append(precipitation_dict)
    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)


    """Return a list for all stations"""
    #query all stations
    results= session.query,(Station.id,Station.station, Sttion.name, Station.latitude, Station.longitude, Station.elevation).all()
    session.close()

    all_stations=[]
    for id,station,name,latitude,longitude,elevation in results:
        station_dict={}
        station_dict['id']=id
        station_dict['station']=station
        station_dict['name']=name
        station_dict['latitude']=latitude
        station_dict['longitude']=longitude
        station_dict[elevation]=elevation
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all Temperature"""
    # Query all precipitation and date
    r_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    st_date=list(np.ravel(r_date))[0]
    latest_date=dt.datetime.strptime(st_date,"%Y-%m-%d")
    year_previous=latest_date-dt.timedelta(days=366)

# Query the last 12 months of temperature observation data for this station
    
    results = session.query(Measurement.date, Measurement.tobs).order_by(Measurement.date.desc()).\
            filter(Measurement.date>=year_previous).all()
    session.close()
    all_temperature=[]
    for tobs, date in results:
        tobs_dict={}
        tobs_dict['date']=date
        tobs_dict['tobs']=tobs
        all_temperature.append(tobs_dict)
    return jsonify(all_temperature)

@app.route("/api/v1.0/<start>/<end>")
def calculated_temp(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    results=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()
    temperature_obs={}
    temperature_obs["Min_Temp"]=results[0][0]
    temperature_obs["avg_Temp"]=results[0][1]
    temperature_obs["max_Temp"]=results[0][2]
    return jsonify(temperature_obs)

@app.route("/api/v1.0/<start>")
def calculated_temp_sd(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    results=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).all()
    session.close()
    temperature_obs={}
    temperature_obs["Min_Temp"]=results[0][0]
    temperature_obs["avg_Temp"]=results[0][1]
    temperature_obs["max_Temp"]=results[0][2]
    return jsonify(temperature_obs)
if __name__ == '__main__':
    app.run(debug=True)