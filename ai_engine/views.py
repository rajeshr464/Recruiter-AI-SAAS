from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
import json
import logging
from datetime import datetime, timedelta

from core.models import Tenant, Candidate, Job
from .models import AIModelMetadata, AIMatchingResult, FeatureExtractionLog, ModelTrainingQueue
from .ml_models.matching import JobCandidateMatchingEngine
from .ml_models.features import ResumeFeatureExtractor

logger = logging.getLogger(__name__)


class AIModelDashboardView(View):
    """
    Dashboard view for AI model management and monitoring
    Shows model performance, training status, and system health
    """
    
    @method_decorator(login_required)
    def get(self, request):
        """
        Render AI dashboard with model statistics and performance metrics
        """
        tenant = request.user.tenant
        
        # Get tenant model metadata
        tenant_model = AIModelMetadata.objects.filter(
            tenant=tenant,
            model_type='tenant',
            status='active'
        ).first()
        
        # Get global model metadata
        global_model = AIModelMetadata.objects.filter(
            tenant=None,
            model_type='global',
            status='active'
        ).first()
        
        # Recent matching results
        recent_matches = AIMatchingResult.objects.filter(
            tenant=tenant
        ).order_by('-created_at')[:10]
        
        # Training queue status
        training_queue = ModelTrainingQueue.objects.filter(
            tenant=tenant,
            status__in=['pending', 'running']
        ).order_by('-created_at')[:5]
        
        # Performance statistics
        match_stats = AIMatchingResult.objects.filter(
            tenant=tenant,
            created_at__gte=datetime.now() - timedelta(days=30)
        ).aggregate(
            avg_score=Avg('match_score'),
            total_matches=Count('id')
        )
        
        context = {
            'tenant_model': tenant_model,
            'global_model': global_model,
            'recent_matches': recent_matches,
            'training_queue': training_queue,
            'match_stats': match_stats,
            'tenant': tenant,
        }
        
        return render(request, 'ai_engine/dashboard.html', context)

class CandidateListView(TemplateView):
    """
    Simple view to render the static candidate list page.
    """
    template_name = "candidate_list.html"


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def find_candidate_matches(request):
    """
    API endpoint to find best candidate matches for a specific job
    Returns ranked list of candidates with match scores
    """
    try:
        data = json.loads(request.body)
        job_id = data.get('job_id')
        limit = data.get('limit', 10)
        
        if not job_id:
            return JsonResponse({
                'error': 'job_id is required'
            }, status=400)
        
        tenant = request.user.tenant
        job = get_object_or_404(Job, id=job_id, tenant=tenant)
        
        # Initialize matching engine
        matching_engine = JobCandidateMatchingEngine(tenant.id)
        
        # Find best matches
        matches = matching_engine.find_best_candidates(job, limit=limit)
        
        # Format response
        response_data = {
            'job_id': job_id,
            'job_title': job.title,
            'matches': matches,
            'total_candidates_scored': len(matches),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Found {len(matches)} candidate matches for job {job_id} (tenant: {tenant.name})")
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error finding candidate matches: {e}")
        return JsonResponse({
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def extract_candidate_features(request):
    """
    API endpoint to extract AI features from candidate resume
    Used for candidate profile enhancement
    """
    try:
        data = json.loads(request.body)
        candidate_id = data.get('candidate_id')
        resume_text = data.get('resume_text', '')
        
        if not candidate_id:
            return JsonResponse({
                'error': 'candidate_id is required'
            }, status=400)
        
        tenant = request.user.tenant
        candidate = get_object_or_404(Candidate, id=candidate_id, tenant=tenant)
        
        # Initialize feature extractor
        extractor = ResumeFeatureExtractor()
        
        # Extract features
        start_time = datetime.now()
        features = extractor.extract_features_from_resume(resume_text, candidate)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Update candidate profile
        candidate.ai_learning_profile = features
        candidate.save()
        
        # Log feature extraction
        FeatureExtractionLog.objects.create(
            tenant=tenant,
            extraction_type='resume',
            entity_id=candidate_id,
            extracted_features=features,
            feature_count=len(features),
            processing_time=processing_time,
            success=True
        )
        
        response_data = {
            'candidate_id': candidate_id,
            'features_extracted': len(features),
            'processing_time': processing_time,
            'features': features,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Extracted {len(features)} features for candidate {candidate_id} (tenant: {tenant.name})")
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error extracting candidate features: {e}")
        return JsonResponse({
            'error': 'Feature extraction failed',
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def retrain_tenant_model(request):
    """
    API endpoint to trigger retraining of tenant-specific AI model
    Queues training job for asynchronous processing
    """
    try:
        tenant = request.user.tenant
        
        # Check if there's already a pending training job
        existing_job = ModelTrainingQueue.objects.filter(
            tenant=tenant,
            training_type__in=['tenant_retrain', 'tenant_initial'],
            status__in=['pending', 'running']
        ).first()
        
        if existing_job:
            return JsonResponse({
                'error': 'Training job already in progress',
                'job_id': existing_job.id,
                'status': existing_job.status
            }, status=409)
        
        # Create new training job
        training_job = ModelTrainingQueue.objects.create(
            tenant=tenant,
            training_type='tenant_retrain',
            status='pending',
            training_config={
                'requested_by': request.user.id,
                'request_time': datetime.now().isoformat()
            }
        )
        
        # TODO: Trigger asynchronous training task (Celery)
        # from .tasks import retrain_tenant_model_task
        # retrain_tenant_model_task.delay(training_job.id)
        
        response_data = {
            'message': 'Training job queued successfully',
            'job_id': training_job.id,
            'tenant': tenant.name,
            'estimated_duration': '10-30 minutes',
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Queued retraining job for tenant {tenant.name} (job_id: {training_job.id})")
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error queuing tenant model retraining: {e}")
        return JsonResponse({
            'error': 'Failed to queue training job',
            'message': str(e)
        }, status=500)


@login_required
def get_model_performance(request):
    """
    API endpoint to get AI model performance metrics
    Returns detailed performance statistics and trends
    """
    try:
        tenant = request.user.tenant
        days = int(request.GET.get('days', 30))
        
        # Get date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get matching results in date range
        matches = AIMatchingResult.objects.filter(
            tenant=tenant,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        # Calculate performance metrics
        performance_data = {
            'total_matches': matches.count(),
            'average_score': matches.aggregate(Avg('match_score'))['match_score__avg'] or 0,
            'average_confidence': matches.aggregate(Avg('confidence'))['confidence__avg'] or 0,
            'score_distribution': {
                'high_score': matches.filter(match_score__gte=0.8).count(),
                'medium_score': matches.filter(match_score__gte=0.5, match_score__lt=0.8).count(),
                'low_score': matches.filter(match_score__lt=0.5).count(),
            },
            'daily_activity': [],
            'feature_performance': {
                'skills_avg': matches.aggregate(Avg('skills_score'))['skills_score__avg'] or 0,
                'experience_avg': matches.aggregate(Avg('experience_score'))['experience_score__avg'] or 0,
                'location_avg': matches.aggregate(Avg('location_score'))['location_score__avg'] or 0,
                'education_avg': matches.aggregate(Avg('education_score'))['education_score__avg'] or 0,
            }
        }
        
        # Get daily activity data
        for i in range(days):
            date = start_date + timedelta(days=i)
            daily_matches = matches.filter(
                created_at__date=date.date()
            )
            
            performance_data['daily_activity'].append({
                'date': date.strftime('%Y-%m-%d'),
                'matches': daily_matches.count(),
                'avg_score': daily_matches.aggregate(Avg('match_score'))['match_score__avg'] or 0
            })
        
        # Get current model info
        current_model = AIModelMetadata.objects.filter(
            tenant=tenant,
            model_type='tenant',
            status='active'
        ).first()
        
        if current_model:
            performance_data['model_info'] = {
                'version': current_model.version,
                'last_trained': current_model.last_trained.isoformat() if current_model.last_trained else None,
                'training_samples': current_model.training_samples,
                'accuracy': current_model.accuracy
            }
        
        return JsonResponse(performance_data)
        
    except Exception as e:
        logger.error(f"Error getting model performance: {e}")
        return JsonResponse({
            'error': 'Failed to get performance data',
            'message': str(e)
        }, status=500)


@login_required
def get_training_status(request):
    """
    API endpoint to get current training job status
    Returns progress and details of ongoing training operations
    """
    try:
        tenant = request.user.tenant
        
        # Get all training jobs for tenant
        training_jobs = ModelTrainingQueue.objects.filter(
            tenant=tenant
        ).order_by('-created_at')[:10]
        
        jobs_data = []
        for job in training_jobs:
            job_data = {
                'id': job.id,
                'training_type': job.training_type,
                'status': job.status,
                'progress': job.progress,
                'current_step': job.current_step,
                'created_at': job.created_at.isoformat(),
                'started_at': job.started_at.isoformat() if job.started_at else None,
                'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                'error_message': job.error_message
            }
            
            if job.result_metadata:
                job_data['results'] = job.result_metadata
            
            jobs_data.append(job_data)
        
        response_data = {
            'training_jobs': jobs_data,
            'active_jobs': len([j for j in jobs_data if j['status'] in ['pending', 'running']]),
            'timestamp': datetime.now().isoformat()
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error getting training status: {e}")
        return JsonResponse({
            'error': 'Failed to get training status',
            'message': str(e)
        }, status=500)


@login_required
def submit_match_feedback(request):
    """
    API endpoint for recruiters to submit feedback on AI matching results
    Used for continuous model improvement and learning
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        match_id = data.get('match_id')
        feedback = data.get('feedback', {})
        outcome = data.get('outcome')
        
        if not match_id:
            return JsonResponse({'error': 'match_id is required'}, status=400)
        
        tenant = request.user.tenant
        match_result = get_object_or_404(
            AIMatchingResult, 
            id=match_id, 
            tenant=tenant
        )
        
        # Update match result with feedback
        match_result.human_feedback = feedback
        if outcome:
            match_result.actual_outcome = outcome
        match_result.save()
        
        # Log feedback for model learning
        logger.info(f"Received feedback for match {match_id} (tenant: {tenant.name})")
        
        return JsonResponse({
            'message': 'Feedback submitted successfully',
            'match_id': match_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error submitting match feedback: {e}")
        return JsonResponse({
            'error': 'Failed to submit feedback',
            'message': str(e)
        }, status=500)
