from flask import Flask
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
from flask_marshmallow import Marshmallow
import config

app = Flask(__name__)

DB_URL = 'postgresql://{user}:{pw}@{url}/{db}'.format(user=config.POSTGRES_USER,pw=config.POSTGRES_PASSWORD,url=config.POSTGRES_HOST,db=config.POSTGRES_DB)

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True # silence the deprecation warning

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

class BikeSchema(ma.Schema):
    class Meta:
        fields = ("id", "lat", "lon", "isReserved", "isDisabled", "createdAt", "lastSeenAtPos", "linger_time_minutes", "linger_time_hours", "linger_time_days")

class Trip(db.Model):
    __tablename__ = 'trips'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.Float)
    end_time = db.Column(db.Float)
    start_latitude = db.Column(db.Float)
    start_longitude = db.Column(db.Float)
    end_latitude = db.Column(db.Float)
    end_longitude = db.Column(db.Float)

#db.create_all()
bikes_schema = BikeSchema(many=True)

@app.route('/')
def hello():
    bikes = Bike.query.all()
    if bikes is None:
        response = {'message': 'user does not exist'}
        return jsonify(response), 404
    result = bikes_schema.dumps(bikes)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
