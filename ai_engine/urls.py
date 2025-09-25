from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import viewsets

# Create DRF router for ViewSets
router = DefaultRouter()
router.register(r'models', viewsets.AIModelMetadataViewSet, basename='ai-models')
router.register(r'matching', viewsets.AIMatchingResultViewSet, basename='ai-matching')
router.register(r'training', viewsets.ModelTrainingQueueViewSet, basename='ai-training')
router.register(r'features', viewsets.FeatureExtractionLogViewSet, basename='ai-features')

app_name = 'ai_engine'

urlpatterns = [
    # Dashboard and main views
    path('', views.AIModelDashboardView.as_view(), name='dashboard'),
    path('dashboard/', views.AIModelDashboardView.as_view(), name='ai_dashboard'),
    path('candidates/', views.CandidateListView.as_view(), name='candidate_list'),
    
    # API endpoints for AJAX calls
    path('api/matches/find/', views.find_candidate_matches, name='find_matches'),
    path('api/features/extract/', views.extract_candidate_features, name='extract_features'),
    path('api/models/retrain/', views.retrain_tenant_model, name='retrain_model'),
    path('api/performance/', views.get_model_performance, name='model_performance'),
    path('api/training/status/', views.get_training_status, name='training_status'),
    path('api/feedback/submit/', views.submit_match_feedback, name='submit_feedback'),
    
    # REST API endpoints (DRF ViewSets)
    path('api/v1/', include(router.urls)),
    
    # Specific AI operations
    path('api/jobs/<int:job_id>/candidates/', views.find_candidate_matches, name='job_candidates'),
    path('api/candidates/<int:candidate_id>/features/', views.extract_candidate_features, name='candidate_features'),
    
    # Model management endpoints
    path('api/models/global/train/', viewsets.AIModelMetadataViewSet.as_view({'post': 'train_global_model'}), name='train_global'),
    path('api/models/tenant/clone/', viewsets.AIModelMetadataViewSet.as_view({'post': 'clone_global_to_tenant'}), name='clone_global'),
    path('api/models/<int:model_id>/validate/', viewsets.AIModelMetadataViewSet.as_view({'post': 'validate_model'}), name='validate_model'),
    
    # Training queue management
    path('api/training/queue/', viewsets.ModelTrainingQueueViewSet.as_view({'get': 'list', 'post': 'create'}), name='training_queue'),
    path('api/training/<int:job_id>/cancel/', viewsets.ModelTrainingQueueViewSet.as_view({'post': 'cancel'}), name='cancel_training'),
    path('api/training/<int:job_id>/restart/', viewsets.ModelTrainingQueueViewSet.as_view({'post': 'restart'}), name='restart_training'),
    
    # Matching and scoring endpoints
    path('api/matching/batch/', viewsets.AIMatchingResultViewSet.as_view({'post': 'batch_match'}), name='batch_match'),
    path('api/matching/score/', viewsets.AIMatchingResultViewSet.as_view({'post': 'calculate_score'}), name='calculate_score'),
    path('api/matching/history/', viewsets.AIMatchingResultViewSet.as_view({'get': 'match_history'}), name='match_history'),
    
    # Feature extraction and analysis
    path('api/features/analyze/', viewsets.FeatureExtractionLogViewSet.as_view({'post': 'analyze_resume'}), name='analyze_resume'),
    path('api/features/compare/', viewsets.FeatureExtractionLogViewSet.as_view({'post': 'compare_profiles'}), name='compare_profiles'),
    path('api/features/trends/', viewsets.FeatureExtractionLogViewSet.as_view({'get': 'feature_trends'}), name='feature_trends'),
    
    # Analytics and reporting endpoints
    path('api/analytics/performance/', views.get_model_performance, name='analytics_performance'),
    path('api/analytics/usage/', viewsets.AIModelMetadataViewSet.as_view({'get': 'usage_analytics'}), name='usage_analytics'),
    path('api/analytics/accuracy/', viewsets.AIModelMetadataViewSet.as_view({'get': 'accuracy_trends'}), name='accuracy_trends'),
    
    # Health check and system status
    path('api/health/', viewsets.AIModelMetadataViewSet.as_view({'get': 'health_check'}), name='health_check'),
    path('api/status/', viewsets.AIModelMetadataViewSet.as_view({'get': 'system_status'}), name='system_status'),
]

# Additional URL patterns for different API versions (future-proofing)
v2_patterns = [
    # Future v2 API endpoints can be added here
    # path('api/v2/', include('ai_engine.api.v2.urls')),
]

urlpatterns += v2_patterns

# Development and debugging URLs (only in DEBUG mode)
try:
    from django.conf import settings
    if settings.DEBUG:
        # Add debugging endpoints that should only be available in development
        debug_patterns = [
            path('debug/model-info/', viewsets.AIModelMetadataViewSet.as_view({'get': 'debug_model_info'}), name='debug_model_info'),
            path('debug/feature-analysis/', viewsets.FeatureExtractionLogViewSet.as_view({'get': 'debug_features'}), name='debug_features'),
            path('debug/training-logs/', viewsets.ModelTrainingQueueViewSet.as_view({'get': 'debug_logs'}), name='debug_training_logs'),
        ]
        urlpatterns += debug_patterns
except ImportError:
    # Handle case where settings might not be available
    pass
