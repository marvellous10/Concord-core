from rest_framework import serializers
from .models import *

class VotingDBSerializer(serializers.Serializer):
    session_name = serializers.CharField(required=True)
    voting_code = serializers.CharField(required=True)
    open_session = serializers.BooleanField(default=False)
    allowed_phone_numbers = serializers.ListField(required=True)
    candidates_voted = serializers.ListField()
    positions = serializers.ListField(required=False)
    
    def create(self, validated_data):
        return VotingDB.objects.create(**validated_data)