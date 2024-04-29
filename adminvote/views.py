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
        host = os.getenv('DATABASE_URI')
        client = MongoClient(host=host, port=27017)
        database = client['voting-system']
        admin_collection = database['AdminUsers']
        admin_user = admin_collection.find_one(
            {
                'phone_number': '08051390089'
            }
        )
        if admin_user:
            #mock data:
            voting_code = [
                {
                    "code": "abcd",
                    "session_name": "test session",
                    "allowed_phone_numbers": [],
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
            admin_collection.update_one(
                {
                    'phone_number': '08051390089'
                },
                {
                    '$set': {
                        'voting_code': voting_code
                    }
                }
            )
            return Response(
                {
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