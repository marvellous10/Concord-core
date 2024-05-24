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
                    'message': 'Successfully added voting data'
                },
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {
                    'status': 'Failed',
                    'message': 'User does not exist'
                },
                status=status.HTTP_404_NOT_FOUND
            )
    
def RecursiveMax(new_array:list, sorted_array:list):
    index = 0
    dict_element = {}
    if len(new_array) == 0:
        return sorted_array
    
    max_voter_count = new_array[0]['voters_number']
        
    for values in range(len(new_array)):
        if max_voter_count < new_array[values]['voters_number']:
            max_voter_count = new_array[values]['voters_number']
            index = values
        else:
            continue
    dict_element = new_array[index]
        
    sorted_array.append(dict_element)
    new_array.pop(index)
    new_list = new_array
    return RecursiveMax(new_list, sorted_array)       

def checkOpenSession(first_list:list, second_list:list):
    if len(first_list) == len(second_list):
        return False
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
            position_winners_list = []
            positions = []
            if checkOpenSession(admin_user_voting_code[code_index]['allowed_phone_numbers'], admin_user_voting_code[code_index]['candidates_voted']) == False:
                update_path = f"voting_code.{code_index}.open_session"
                admin_collection.update_one(
                    {
                        'phone_number': phone_number
                    },
                    {
                        '$set': {
                            update_path: False
                        }
                    },
                    upsert = False
                )
            open_session = admin_user_voting_code[code_index]['open_session']
            #voters_max = len(admin_positions[0]['candidates'][0]['voters'])
            for voters in range(len(admin_positions[0]['candidates'])):
                voters_count += len(admin_positions[0]['candidates'][voters]['voters'])
            total_voter_count = f"{voters_count}"
            for voters in range(len(admin_positions)):
                position_dict = {
                    "id": "",
                    "name": ""
                }
                position_dict['id'] = admin_positions[voters]['id']
                position_dict['name'] = admin_positions[voters]['name']
                positions.append(position_dict)
                voters_max = len(admin_positions[voters]['candidates'][0]['voters'])
                new_list = []
                for votes in range(len(admin_positions[voters]['candidates'])):
                    result_dict = {
                        "name": "",
                        "id": "",
                        "voters_number": ""
                    }
                    result_dict['name'] = admin_positions[voters]['candidates'][votes]['name']
                    result_dict['id'] = admin_positions[voters]['candidates'][votes]['id']
                    result_dict['voters_number'] = len(admin_positions[voters]['candidates'][votes]['voters'])
                    new_list.append(result_dict)
                position_winners.append(new_list)
            for val in range(len(admin_positions)):
                sorted_array = [] * len(admin_positions[val]['candidates'])
                RecursiveMax(position_winners[val], sorted_array)
                position_winners_list.append(sorted_array)
            return Response(
                {
                    "status": "Passed",
                    "session_name": session_name,
                    "voting_code": admin_voting_code,
                    "open_session": open_session,
                    "position_count": str(admin_positions_length),
                    "voters_count": total_voter_count,
                    "positions": positions,
                    "position_winners": position_winners_list
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
        
class ChangeSessionStatus(APIView):
    def post(self, request, format=None, *args, **kwargs):
        access_token = request.data.get('access_token')
        status_data = request.data.get('status')
        voting_code = request.data.get('voting_code')
        
        load_dotenv()
        decoded_token = jwt.decode(access_token, os.getenv('JWT_ENCODING_KEY'), algorithms=['HS256'])
        phone_number = decoded_token['message_info']['phone_number']
        admin_access = decoded_token['message_info']['admin']
        
        if admin_access != True:
            return Response(
                {
                    'status': 'Failed',
                    'message': 'You are not allowed to change the status'
                },
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        try:
            host = os.getenv('DATABASE_URI')
            client = MongoClient(host=host, port=27017)
            database = client['voting-system']
            admin_collection = database['AdminUsers']
            admin_user = admin_collection.find_one(
                {
                    'phone_number': phone_number
                }
            )
        except Exception as e:
            return Response(
                {
                    'status': 'Failed',
                    'message': 'An error occurred please try again'
                },
                status=status.HTTP_408_REQUEST_TIMEOUT
            )
        
        code_index = 0
        if admin_user:
            code = ''
            for details in range(len(admin_user['voting_code'])):
                code = admin_user['voting_code'][details]['code']
                if voting_code == code:
                    code_index = details
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
            
            update_path = f"voting_code.{code_index}.open_session"
            try:
                admin_collection.update_one(
                    {'phone_number': phone_number},
                    {'$set': {update_path: status_data}},
                    upsert=False
                )
                if status_data == True:
                    return Response(
                        {
                            'status': 'Passed',
                            'message': 'Session is now open'
                        },
                        status=status.HTTP_202_ACCEPTED
                    )
                else:
                   return Response(
                        {
                            'status': 'Passed',
                            'message': 'Session is now closed'
                        },
                        status=status.HTTP_202_ACCEPTED
                    ) 
            except Exception as e:
                return Response(
                    {
                        'status': 'Failed',
                        'message': 'An error occured, please try again'
                    },
                    status=status.HTTP_409_CONFLICT
                )
        else:
            return Response(
                {
                    'status': 'Failed',
                    'message': 'User does not exist'
                },
                status=status.HTTP_404_NOT_FOUND
            )
            