from flask import Flask
from flask import Response
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
from flask_marshmallow import Marshmallow
from marshmallow import post_dump, pre_dump
import time
import config

app = Flask(__name__)

DB_URL = 'postgresql://{user}:{pw}@{url}/{db}'.format(user=config.POSTGRES_USER,pw=config.POSTGRES_PASSWORD,url=config.POSTGRES_HOST,db=config.POSTGRES_DB)

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True # silence the deprecation warning
app.config['JSON_SORT_KEYS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Bike(db.Model):
    __tablename__ = 'bikes'

    id = db.Column(db.Integer, primary_key=True)
    lat = db.Column(db.String())
    lon = db.Column(db.String())
    isReserved = db.Column(db.Integer)
    isDisabled = db.Column(db.Integer)
    createdAt = db.Column(db.String())
    lastSeenAtPos = db.Column(db.Float)
    linger_time_minutes = db.Column(db.Float)
    linger_time_hours = db.Column(db.Float)
    linger_time_days = db.Column(db.Float)

class BikeSchema(ma.ModelSchema):
    class Meta:
        model = Bike
    @post_dump(pass_many=True)
    def geojson(self, data, many):
        points = []
        for point in data:
            pointdata = {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [float(point['lon']), float(point['lat'])]}, 'properties': {'linger_time_hours': point['linger_time_hours']}}
            points.append(pointdata)
        formatteddata = {'type': 'FeatureCollection', 'features': points}
        return formatteddata

class Trip(db.Model):
    __tablename__ = 'trips'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.Float)
    end_time = db.Column(db.Float)
    start_latitude = db.Column(db.Float)
    start_longitude = db.Column(db.Float)
    end_latitude = db.Column(db.Float)
    end_longitude = db.Column(db.Float)

class TripSchema(ma.ModelSchema):
    class Meta:
        model = Trip
        additional = ("lat", "lon")
    @post_dump(pass_many=True)
    def geojson(self, data, many):
        points = []
        for point in data:
            pointdata = {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [float(point['lon']), float(point['lat'])]}, 'properties': {}}
            points.append(pointdata)
        return points

#db.create_all()
bikes_schema = BikeSchema(many=True)
trips_schema = TripSchema(many=True)

@app.route(config.PROXY_PASS + '/bikes')
def bikes():
    bikes = Bike.query.with_entities(Bike.lat, Bike.lon, Bike.linger_time_hours).filter(Bike.linger_time_hours < 150)
    if bikes is None:
        response = {'message': 'there are no bikes in the db'}
        return jsonify(response), 404
    def generate():
        points = bikes.__iter__()
        try:
            prev_point = next(points)  # get first result
        except StopIteration:
            # StopIteration here means the length was zero, so yield a valid releases doc and stop
            yield '{"releases": []}'
            raise StopIteration
        # We have some releases. First, yield the opening json
        yield '{"type": "FeatureCollection", "features": ['
        # Iterate over the releases
        for point in points:
            yield '{"type": "Feature", "geometry": {"type": "Point", "coordinates": [' + str(point[1]) + ',' + str(point[0]) + ']}, "properties": {"linger_time_hours": ' + str(point[2]) + '}}' + ', '
            prev_point = point
        # Now yield the last iteration without comma but with the closing brackets
        yield '{"type": "Feature", "geometry": {"type": "Point", "coordinates": [' + str(point[1]) + ',' + str(point[0]) + ']}, "properties": {"linger_time_hours": ' + str(point[2]) + '}}' + ']}'
    return Response(generate(), mimetype='application/json', headers={"Access-Control-Allow-Origin": "*"})

@app.route(config.PROXY_PASS + '/trips/<string:from_where>')
def trip(from_where):
    #from_where = 'origin'
    lastday = int(time.time() * 1000) - 86400000
    if from_where == 'origin':
        trips = Trip.query.with_entities(Trip.start_latitude.label('lat'), Trip.start_longitude.label('lon')).filter(Trip.end_time > lastday, Trip.start_latitude != None)
    elif from_where == 'destination':
        trips = Trip.query.with_entities(Trip.end_latitude.label('lat'), Trip.end_longitude.label('lon')).filter(Trip.end_time > lastday, Trip.start_latitude != None)
    if trips is None:
        response = {'message': 'No trips'}
        return jsonify(response), 404
    def generate():
        points = trips.__iter__()
        try:
            prev_point = next(points)  # get first result
        except StopIteration:
            # StopIteration here means the length was zero, so yield a valid releases doc and stop
            yield '{"releases": []}'
            raise StopIteration
        # We have some releases. First, yield the opening json
        yield '{"type": "FeatureCollection", "features": ['
        # Iterate over the releases
        for point in points:
            yield '{"type": "Feature", "geometry": {"type": "Point", "coordinates": [' + str(point[1]) + ',' + str(point[0]) + ']}, "properties": {}}' + ', '
            prev_point = point
        # Now yield the last iteration without comma but with the closing brackets
        yield '{"type": "Feature", "geometry": {"type": "Point", "coordinates": [' + str(point[1]) + ',' + str(point[0]) + ']}, "properties": {}}' + ']}'
    return Response(generate(), mimetype='application/json', headers={"Access-Control-Allow-Origin": "*"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
