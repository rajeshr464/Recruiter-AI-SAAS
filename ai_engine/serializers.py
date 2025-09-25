# ai_engine/serializers.py

from rest_framework import serializers
from ai_engine.models import (
    AIModelMetadata,
    FeatureExtractionLog,
    AIMatchingResult,
    ModelTrainingQueue
)

class AIModelMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIModelMetadata
        fields = '__all__'

class FeatureExtractionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureExtractionLog
        fields = '__all__'

class AIMatchingResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIMatchingResult
        fields = '__all__'

class ModelTrainingQueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelTrainingQueue
        fields = '__all__'
