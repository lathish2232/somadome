import os
from email.mime import audio

from flask import Flask, jsonify, request, send_file, render_template, Response
from flask_restful import Api
from flask_jwt_extended import JWTManager
from io import BytesIO

# from blacklist import BLACKLIST
from werkzeug.utils import secure_filename

from automate_methods import create_presigned_url
from blacklist import BLACKLIST
from db import db
from ma import ma
from models.image import Img
from models.mood_tracker import Songs
from models.somadom_models import Tier,Category,Content
from resources.user import UserRegister, UserLogin, UserLogout, User, TokenRefresh

from resources.somadome_resource import GetSessionHistory,GetSessionMetrics,GetContent,GetDomAvailability,FindDoms

app = Flask(__name__)

#uri = os.getenv("DATABASE_URL", 'sqlite:///data.db')  # or other relevant config var
uri = 'postgresql://postgres:12345@localhost/somadome_db'
#if uri.startswith("postgres://"):
#    uri = uri.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = uri
# app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config['JWT_BLACKLIST_ENABLED'] = True  # enable blacklist feature
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']  # allow blacklisting for access and refresh tokens

app.secret_key = "somadome"  # could do app.config['JWT_SECRET_KEY'] if we prefer
api = Api(app)

jwt = JWTManager(app)

@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_headers, jwt_payload):
    return jwt_payload['jti'] in BLACKLIST


@jwt.revoked_token_loader
def revoked_token_callback(jwt_headers, jwt_payload):
    return jsonify({
        'description': 'the token has been revoked.',
        'error': 'token revoked'
    }), 401


@app.route('/upload', methods=['POST'])
def upload():
    entityType = request.args.get('entityType')
    entityId = request.args.get('entityId')
    replace = bool(request.args.get('replace'))
    index = request.args.get('index')
    imageData = request.files['imageData']
    if not imageData:
        return 'No pic uploaded!', 400

    filename = secure_filename(imageData.filename)
    mimetype = imageData.mimetype
    if not filename or not mimetype:
        return 'Bad upload!', 400

    # img = Img(img=pic.read(), name=filename, mimetype=mimetype)
    img = Img(entityType=entityType, entityId=entityId, replace=replace, index=index, imageData=imageData.read())
    db.session.add(img)
    db.session.commit()

    return 'Img Uploaded!', 200


@app.route("/music/", methods=['get'])
def musicis():
    musictype = request.args.get('musictype')
    objectname=musictype+".mp3"
    return create_presigned_url('smarttracmusic',objectname)


api.add_resource(UserRegister, "/register")
api.add_resource(User, "/user/profile")
api.add_resource(UserLogin, "/login")
api.add_resource(TokenRefresh, "/refresh")
api.add_resource(UserLogout, "/logout")
api.add_resource(GetSessionHistory, "/session/history") #get Session history
api.add_resource(GetSessionMetrics, "/session/metrics") #get Session Metrics
api.add_resource(GetContent, "/getcontent")#get content 
api.add_resource(GetDomAvailability,"/dome/availability") # getdome availability
api.add_resource(FindDoms,"/dome/find") # find public domes 
#api.add_resource(CreateReservation,"/reservation")



db.init_app(app)
ma.init_app(app)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
