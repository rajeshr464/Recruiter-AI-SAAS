from django.db import models
from django.contrib.auth import get_user_model
from core.models import Tenant
import json

User = get_user_model()


class AIModelMetadata(models.Model):
    """
    Metadata for AI models (global and tenant-specific)
    Tracks model versions, performance metrics, and training history
    """
    MODEL_TYPES = [
        ('global', 'Global AI Model'),
        ('tenant', 'Tenant-Specific Model'),
    ]
    
    STATUS_CHOICES = [
        ('training', 'Training'),
        ('active', 'Active'),
        ('deprecated', 'Deprecated'),
        ('failed', 'Failed'),
    ]
    
    tenant = models.ForeignKey(
        Tenant, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        help_text="Null for global models"
    )
    model_type = models.CharField(max_length=20, choices=MODEL_TYPES)
    model_path = models.CharField(max_length=512)
    version = models.CharField(max_length=50, default='1.0.0')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='training')
    
    # Performance metrics
    accuracy = models.FloatField(null=True, blank=True)
    precision = models.FloatField(null=True, blank=True)
    recall = models.FloatField(null=True, blank=True)
    f1_score = models.FloatField(null=True, blank=True)
    
    # Training metadata
    training_samples = models.IntegerField(default=0)
    training_duration = models.DurationField(null=True, blank=True)
    features_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_trained = models.DateTimeField(null=True, blank=True)
    
    # Configuration and hyperparameters
    hyperparameters = models.JSONField(default=dict, blank=True)
    feature_config = models.JSONField(default=dict, blank=True)
    
    class Meta:
        unique_together = ['tenant', 'model_type', 'version']
        ordering = ['-created_at']
        
    def __str__(self):
        if self.tenant:
            return f"{self.tenant.name} - {self.model_type} v{self.version}"
        return f"Global - {self.model_type} v{self.version}"
    
    def get_performance_summary(self):
        """
        Get a summary of model performance metrics
        """
        return {
            'accuracy': self.accuracy,
            'precision': self.precision,
            'recall': self.recall,
            'f1_score': self.f1_score,
            'training_samples': self.training_samples
        }


class FeatureExtractionLog(models.Model):
    """
    Log of feature extraction operations for audit and debugging
    """
    EXTRACTION_TYPES = [
        ('resume', 'Resume Text'),
        ('job', 'Job Description'),
        ('candidate', 'Candidate Profile'),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    extraction_type = models.CharField(max_length=20, choices=EXTRACTION_TYPES)
    entity_id = models.IntegerField()  # ID of candidate, job, etc.
    
    # Feature extraction results
    extracted_features = models.JSONField(default=dict)
    feature_count = models.IntegerField(default=0)
    processing_time = models.FloatField(help_text="Processing time in seconds")
    
    # Status and error handling
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'extraction_type']),
            models.Index(fields=['entity_id', 'extraction_type']),
        ]
    
    def __str__(self):
        return f"{self.tenant.name} - {self.extraction_type} extraction for {self.entity_id}"


class AIMatchingResult(models.Model):
    """
    Results of AI-powered job-candidate matching
    Stores matching scores and reasoning for audit and learning
    """
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    job_id = models.IntegerField()
    candidate_id = models.IntegerField()
    
    # Matching results
    match_score = models.FloatField(help_text="0.0 to 1.0 matching score")
    confidence = models.FloatField(help_text="0.0 to 1.0 confidence level")
    
    # Detailed scoring breakdown
    skills_score = models.FloatField(default=0.0)
    experience_score = models.FloatField(default=0.0)
    location_score = models.FloatField(default=0.0)
    education_score = models.FloatField(default=0.0)
    
    # AI reasoning and explainability
    reasoning = models.JSONField(
        default=dict,
        help_text="AI reasoning for the match score"
    )
    feature_importance = models.JSONField(
        default=dict,
        help_text="Feature importance weights used in scoring"
    )
    
    # Model information
    model_version = models.CharField(max_length=50)
    ai_model = models.ForeignKey(
        AIModelMetadata, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    # Feedback and learning
    human_feedback = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Recruiter feedback for model learning"
    )
    actual_outcome = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        help_text="Actual hiring outcome for learning"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['tenant', 'job_id', 'candidate_id']
        ordering = ['-match_score', '-created_at']
        indexes = [
            models.Index(fields=['tenant', 'job_id', '-match_score']),
            models.Index(fields=['tenant', 'candidate_id']),
        ]
    
    def __str__(self):
        return f"{self.tenant.name} - Job {self.job_id} x Candidate {self.candidate_id} ({self.match_score:.2f})"
    
    def get_score_breakdown(self):
        """
        Get detailed breakdown of matching scores
        """
        return {
            'overall_score': self.match_score,
            'confidence': self.confidence,
            'breakdown': {
                'skills': self.skills_score,
                'experience': self.experience_score,
                'location': self.location_score,
                'education': self.education_score,
            }
        }


class ModelTrainingQueue(models.Model):
    """
    Queue for asynchronous AI model training tasks
    Manages training jobs for both global and tenant models
    """
    TRAINING_TYPES = [
        ('global_initial', 'Initial Global Training'),
        ('global_retrain', 'Global Model Retraining'),
        ('tenant_initial', 'Initial Tenant Training'),
        ('tenant_retrain', 'Tenant Model Retraining'),
        ('tenant_clone', 'Clone Global to Tenant'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    tenant = models.ForeignKey(
        Tenant, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        help_text="Null for global training tasks"
    )
    training_type = models.CharField(max_length=30, choices=TRAINING_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Training configuration
    training_config = models.JSONField(
        default=dict,
        help_text="Training parameters and configuration"
    )
    
    # Progress tracking
    progress = models.IntegerField(default=0, help_text="0-100 percentage")
    current_step = models.CharField(max_length=100, blank=True)
    
    # Results and error handling
    result_metadata = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Associated model
    ai_model = models.ForeignKey(
        AIModelMetadata,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['tenant', 'training_type']),
        ]
    
    def __str__(self):
        tenant_name = self.tenant.name if self.tenant else "Global"
        return f"{tenant_name} - {self.training_type} ({self.status})"