from flask import Flask, request, Response
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

application = app = Flask(__name__)
CORS(app)
api = Api(app)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:TrickyPassword@localhost/DoctorDb'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://ronknighton@doctor-api-db-svr:R0na!d1966@doctor-api-db-svr.mysql.database.azure.com/doctordb'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://ronknighton:R0na!d1966@doctorapi-db.ceztmqgtoqb1.us-east-2.rds.amazonaws.com/doctordb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_POOL_PRE_PING'] = True
db = SQLAlchemy(app)
# db.init_app(app)






