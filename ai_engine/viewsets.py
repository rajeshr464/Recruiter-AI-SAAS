from rest_framework import viewsets
from ai_engine.models import (
    AIModelMetadata,
    FeatureExtractionLog,
    AIMatchingResult,
    ModelTrainingQueue,
)
from ai_engine.serializers import (
    AIModelMetadataSerializer,
    FeatureExtractionLogSerializer,
    AIMatchingResultSerializer,
    ModelTrainingQueueSerializer,
)

class AIModelMetadataViewSet(viewsets.ModelViewSet):
    queryset = AIModelMetadata.objects.all()
    serializer_class = AIModelMetadataSerializer

class FeatureExtractionLogViewSet(viewsets.ModelViewSet):
    queryset = FeatureExtractionLog.objects.all()
    serializer_class = FeatureExtractionLogSerializer

class AIMatchingResultViewSet(viewsets.ModelViewSet):
    queryset = AIMatchingResult.objects.all()
    serializer_class = AIMatchingResultSerializer

class ModelTrainingQueueViewSet(viewsets.ModelViewSet):
    queryset = ModelTrainingQueue.objects.all()
    serializer_class = ModelTrainingQueueSerializer
