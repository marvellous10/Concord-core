from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

import os
from dotenv import load_dotenv
from datetime import datetime as dt, timedelta, timezone
import jwt
from pymongo import MongoClient

from .models import *
from .serializers import *


class AddPosition(APIView):
    def post(self, request, format=None, *args, **kwargs):
        load_dotenv()
        access_token = request.data.get('access_token')
        votingdata = request.data.get('voting_data')
        try:
            decoded_token = jwt.decode(access_token, os.getenv('JWT_ENCODING_KEY'), algorithms=['HS256'])
        except jwt.ExpiredSignatureError as jwte:
            return Response(
                {
                    'status': 'Failed',
                    'message': 'Please Log in again'
                },
                status=status.HTTP_406_NOT_ACCEPTABLE
            )
        phone_number = decoded_token['message_info']['phone_number']
        admin_access = decoded_token['message_info']['admin']
        if admin_access != True:
            return Response(
                {
                    'status': 'Failed',
                    'message': 'You are not allowed to create a session'
                },
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
            
        host = os.getenv('DATABASE_URI')
        client = MongoClient(host=host, port=27017)
        database = client['voting-system']
        admin_collection = database['AdminUsers']
        admin_user = admin_collection.find_one(
            {
                'phone_number': phone_number
            }
        )
        if admin_user:
            #mock data:
            '''voting_code = [
                {
                    "code": "abcd",
                    "session_name": "test session",
                    "allowed_phone_numbers": ['08051390081', '07049195356'],
                    "candidates_voted": [],
                    "positions": [
                        {
                            "id": "werer",
                            "name": "president test",
                            "candidates": [
                                {
                                    "id": "1",
                                    "name": "testcan 1",
                                    "voters": []
                                },
                                {
                                    "id": "2",
                                    "name": "testcan 2",
                                    "voters": []
                                }
                            ]
                        },
                        {
                            "id": "wer12",
                            "name": "vice president test",
                            "candidates": [
                                {
                                    "id": "1",
                                    "name": "testcan 1",
                                    "voters": []
                                },
                                {
                                    "id": "2",
                                    "name": "testcan 2",
                                    "voters": []
                                }
                            ]
                        }
                    ]
                }
            ]
            '''
            admin_collection.update_one(
                {
                    'phone_number': phone_number
                },
                {
                    '$push': {
                        'voting_code': votingdata
                    }
                }
            )
            return Response(
                {
                    'status': 'Passed',
                    'message': 'Successfully added voting code'
                },
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {
                    'message': 'User does not exist'
                },
                status=status.HTTP_404_NOT_FOUND
            )
            
class Overview(APIView):
    def post(self, request, format=None, *args, **kwargs):
        voting_code = request.data.get('voting_code')
        access_token = request.data.get('access_token')
        load_dotenv()
        decoded_token = jwt.decode(access_token, os.getenv('JWT_ENCODING_KEY'), algorithms=['HS256'])
        phone_number = decoded_token['message_info']['phone_number']
        admin_access = decoded_token['message_info']['admin']
        if admin_access != True:
            return Response(
                {
                    'status': 'Failed',
                    'message': 'You are not allowed to access this code'
                }
            )
        host = os.getenv('DATABASE_URI')
        client = MongoClient(host=host, port=27017)
        database = client['voting-system']
        admin_collection = database['AdminUsers']
        admin_user = admin_collection.find_one(
            {
                'phone_number': phone_number
            }
        )
        #voting_detail = {}
        code_index = 0
        if admin_user:
            code = ''
            for det in range(len(admin_user['voting_code'])):
                code = admin_user['voting_code'][det]['code']
                if voting_code == admin_user['voting_code'][det]['code']:
                    code = voting_code
                    code_index = det
                    break
                else: continue
            if code != voting_code:
                return Response(
                    {
                        'status': 'Failed',
                        'message': 'The code does not exist'
                    },
                    status=status.HTTP_406_NOT_ACCEPTABLE
                )
            admin_user_voting_code = admin_user['voting_code']
            session_name = admin_user_voting_code[code_index]['session_name']
            admin_voting_code = admin_user_voting_code[code_index]['code']
            admin_positions = admin_user_voting_code[code_index]['positions']
            admin_positions_length = len(admin_positions)
            voters_count = 0
            position_winners = []
            positions = []               
            #voters_max = len(admin_positions[0]['candidates'][0]['voters'])
            for voters in range(len(admin_positions[0]['candidates'])):
                voters_count += len(admin_positions[0]['candidates'][voters]['voters'])
            total_voter_count = f"{voters_count}"
            for voters in range(len(admin_positions)):
                result_dict = {
                    "name": "",
                    "id": "",
                    "voters_number": ""
                }
                position_dict = {
                    "id": "",
                    "name": ""
                }
                position_dict['id'] = admin_positions[voters]['id']
                position_dict['name'] = admin_positions[voters]['name']
                positions.append(position_dict)
                voters_max = len(admin_positions[voters]['candidates'][0]['voters'])
                for votes in range(len(admin_positions[voters]['candidates'])):
                    if voters_max < len(admin_positions[voters]['candidates'][votes]['voters']):
                        voters_max = len(admin_positions[voters]['candidates'][votes]['voters'])
                        result_dict['name'] = admin_positions[voters]['candidates'][votes]['name']
                        result_dict['id'] = admin_positions[voters]['candidates'][votes]['id']
                        result_dict['voters_number'] = len(admin_positions[voters]['candidates'][votes]['voters'])
                    elif voters_max > len(admin_positions[voters]['candidates'][votes]['voters']):
                        result_dict['name'] = admin_positions[voters]['candidates'][0]['name']
                        result_dict['id'] = admin_positions[voters]['candidates'][0]['id']
                        result_dict['voters_number'] = len(admin_positions[voters]['candidates'][0]['voters'])
                position_winners.append(result_dict)
            print(position_winners)
            return Response(
                {
                    "status": "Passed",
                    "session_name": session_name,
                    "voting_code": admin_voting_code,
                    "position_count": str(admin_positions_length),
                    "voters_count": total_voter_count,
                    "positions": positions,
                    "position_winners": position_winners
                },
                status=status.HTTP_200_OK
            )  
        return Response(
            {
                'status': 'Failed',
                'message': 'User does not exist'
            },
            status=status.HTTP_406_NOT_ACCEPTABLE
        )  
        
        