from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

import jwt
import os
from datetime import datetime as dt, timedelta, timezone
from pymongo import MongoClient
from dotenv import load_dotenv

from adminvote.models import *
from adminvote.serializers import *



class CandidateVote(APIView):
    def post(self, request, format=None, *args, **kwargs):
        load_dotenv()
        selected_data = request.data.get('selected_data')
        access_token = request.data.get('access_token')
        voting_code = request.data.get('voting_code')
        
        decoded_token = jwt.decode(access_token, os.getenv('JWT_ENCODING_KEY'), algorithms=['HS256'])
        phone_number = decoded_token['message_info']['phone_number']
        admin_access = decoded_token['message_info']['admin']
        if admin_access == True:
            return Response(
                {
                    'status': 'Failed',
                    'message': "Seems you cannot vote with this number"
                },
                status=status.HTTP_406_NOT_ACCEPTABLE
            )
        try:
            host = os.getenv('DATABASE_URI')
            client = MongoClient(host=host, port=27017)
            database = client['voting-system']
            candidate_collection = database['CandidateUsers']
            candidate_user = candidate_collection.find_one(
                {
                    'phone_number': phone_number
                }
            )
        except Exception as e:
            return Response(
                {
                    'status': 'Failed',
                    'message': 'An error occurred while checking for user, try again later'
                },
                status=status.HTTP_408_REQUEST_TIMEOUT
            )
        if candidate_user:
            '''admin_collection = database['AdminUsers']
            admin_user = admin_collection.find_one(
                {
                    'phone_number': admin_user_phone_number
                }
            )'''
            votingdb_session_details = VotingDB.objects.filter(voting_code=voting_code).first()
            if votingdb_session_details:
                voting_session_serializer_detail = VotingDBSerializer(votingdb_session_details)
                voting_details = voting_session_serializer_detail.data
            else:
                return Response(
                    {
                        'status': 'Failed',
                        'message': 'The voting code does not exist'
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            voting_code_list = voting_details['voting_code']
            if phone_number not in voting_details['allowed_phone_numbers']:
                return Response(
                    {
                        'status': 'Failed',
                        'message': 'You are not allowed to vote'
                    },
                    status=status.HTTP_405_METHOD_NOT_ALLOWED
                )
            if phone_number in voting_details['candidates_voted']:
                return Response(
                    {
                        'status': 'Failed',
                        'message': 'You have already voted'
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            if voting_details['open_session'] == False:
                return Response(
                    {
                        'status': 'Failed',
                        'message': 'Voting session is closed right now'
                    },
                    status=status.HTTP_405_METHOD_NOT_ALLOWED
                )
            positions = voting_details['positions']
            voted = False
            for position in range(len(positions)):
                candidate_id = selected_data[position]
                # Find the candidate index based on the candidate ID
                candidate_index = next((index for index, candidate in enumerate(positions[position]['candidates']) if candidate['id'] == candidate_id), None)
                      
                if candidate_index is not None:
                    if phone_number not in voting_details['candidates_voted']:
                        votingdb_session_details['positions'][position]['candidates'][candidate_index]['voters'].append(phone_number)
                        votingdb_session_details.save()
                        voted=True
            #voting_code_path = f"voting_code.{code_index}.candidates_voted"
            if voted == True:
                votingdb_session_details['candidates_voted'].append(phone_number)
                votingdb_session_details.save()
                return Response(
                    {
                        'status': 'Passed',
                        'message': 'Voting Done'
                    },
                    status=status.HTTP_202_ACCEPTED
                )
            else:
                return Response(
                    {
                        'status': 'Failed',
                        'message': 'No admin noted'
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                )
        else:
            return Response(
                {
                    'status': 'Failed',
                    'message': 'Cannot find user'
                },
                status=status.HTTP_404_NOT_FOUND
            )
                            
                