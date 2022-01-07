import json

from datetime import datetime
import re


from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt,
    get_jwt_identity)
from werkzeug.security import safe_str_cmp
from marshmallow import ValidationError

from blacklist import BLACKLIST
from db import db
from models.somadom_models import Availability, Content, Session, Tier
from util.http_response import success_response,user_not_found,dome_not_found


class GetSessionHistory(Resource):
    @classmethod
    #@jwt_required(fresh=True)
    def post(cls):
        req_body=reqparse.request.get_json()['params']
        session_history = Session.find_by_id(req_body['userId'])
        if not session_history:
            return user_not_found, 404
        data={}
        data['sessions']=[ row.json_fmt() for row in session_history]
        data=json.loads(json.dumps(data,indent=4, sort_keys=True, default=str))
        print(data)
        return success_response(result=data), 200

class GetSessionMetrics(Resource):
    @classmethod
    #@jwt_required(fresh=True)
    def post(cls):
        req_body=reqparse.request.get_json()['params']
        session_metrics = Session.find_session_in_pastdays(req_body['userId'],req_body['pastDays'])
        if not session_metrics:
            return user_not_found, 404
        return success_response(result=session_metrics), 200
        
class GetContent(Resource):
    @classmethod
    #@jwt_required(fresh=True)
    def post(cls):
        req_body=reqparse.request.get_json()['params']
        content_data = Content.get_content(req_body['userId'])
        tier_id = Tier.get_tier_ids()
        if not content_data:
            return user_not_found, 404
        
        result={"userTiers":tier_id}
        data={"categories":[]}
        for rec in content_data:
            if rec[0]:
                content_rows= rec[0].json_fmt()
            data['categories'].append({"name":rec[1],"imageUrl":rec[2],"contents":[]})
            
            data['categories'][0]['contents'].append({"ownerName":rec[3],
                                                 "ownerDescription":rec[4],
                                                 "ownerImageUrl":rec[5],
                                                 "contentId":content_rows['contentId'],
                                                 "duration":content_rows['duration'],
                                                 "title":content_rows['title'],
                                                 "description":content_rows['description'],
                                                 "tier":rec[6],
                                                 "imageUrl":content_rows['imageUrl'],
                                                 "audioUrl":content_rows['audioUrl']})
        result.update(data)
        return success_response(result=result), 200

class GetDomAvailability(Resource):
    @classmethod
    #@jwt_required(fresh=True)
    def post(cls):

        req_body=reqparse.request.get_json()['params']
        dome_data = Availability.find_dome_availability(req_body['domeId'],req_body['date'],req_body['time'])
        if not dome_data:
            return dome_not_found, 404
        
        result=[]
        for rec in dome_data:
            result.append({"data":rec[0].isoformat(),
                         "startTime":rec[1].isoformat(),
                        "endTime":rec[2].isoformat()})

        data={'domeId':req_body['domeId']}
        data['availability']=result
        return success_response(result=data), 200
    
class FindDoms(Resource):

    @classmethod
    #@jwt_required(fresh=True)
    def post(cls):
        req_body=reqparse.request.get_json()['params']
        userLocation = req_body['userLocation']
        distance = req_body['req_body']
        data = req_body['date']
        time =req_body['time']
        duration = req_body['duration']
        dome_data = Availability.find_dome_availability(req_body['domeId'],req_body['date'],req_body['time'])




