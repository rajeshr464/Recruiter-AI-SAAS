from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db import models
from django.contrib import messages
import json
from datetime import datetime

from .models import (
    AIModelMetadata, 
    FeatureExtractionLog, 
    AIMatchingResult, 
    ModelTrainingQueue
)


@admin.register(AIModelMetadata)
class AIModelMetadataAdmin(admin.ModelAdmin):
    """
    Django Admin interface for AI Model Metadata management
    Provides comprehensive view of model performance and status
    """
    
    list_display = [
        'model_display', 'tenant_name', 'model_type', 'version', 
        'status', 'accuracy_display', 'training_samples', 'last_trained'
    ]
    
    list_filter = [
        'model_type', 'status', 'created_at', 'tenant__subscription_plan'
    ]
    
    search_fields = [
        'tenant__name', 'version', 'model_path'
    ]
    
    readonly_fields = [
        'created_at', 'updated_at', 'performance_metrics_display',
        'hyperparameters_display', 'feature_config_display'
    ]
    
    fieldsets = (
        ('Model Information', {
            'fields': ('tenant', 'model_type', 'model_path', 'version', 'status')
        }),
        ('Performance Metrics', {
            'fields': (
                'accuracy', 'precision', 'recall', 'f1_score',
                'performance_metrics_display'
            ),
            'classes': ('collapse',)
        }),
        ('Training Information', {
            'fields': (
                'training_samples', 'training_duration', 'features_count',
                'last_trained'
            ),
            'classes': ('collapse',)
        }),
        ('Configuration', {
            'fields': (
                'hyperparameters_display', 'feature_config_display'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def model_display(self, obj):
        """Custom display for model with status indicator"""
        status_colors = {
            'active': '#28a745',
            'training': '#ffc107',
            'deprecated': '#6c757d',
            'failed': '#dc3545'
        }
        color = status_colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">● {}</span>',
            color,
            f"{obj.model_type.title()} v{obj.version}"
        )
    model_display.short_description = 'Model'
    
    def tenant_name(self, obj):
        """Display tenant name or 'Global' for global models"""
        return obj.tenant.name if obj.tenant else 'Global'
    tenant_name.short_description = 'Tenant'
    
    def accuracy_display(self, obj):
        """Display accuracy with color coding"""
        if obj.accuracy is None:
            return mark_safe('<span style="color: #6c757d;">N/A</span>')
        
        color = '#28a745' if obj.accuracy >= 0.8 else '#ffc107' if obj.accuracy >= 0.6 else '#dc3545'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1%}</span>',
            color,
            obj.accuracy
        )
    accuracy_display.short_description = 'Accuracy'
    
    def performance_metrics_display(self, obj):
        """Display performance metrics in a formatted table"""
        if not any([obj.accuracy, obj.precision, obj.recall, obj.f1_score]):
            return "No performance data available"
        
        metrics_html = """
        <table style="width: 100%; border-collapse: collapse;">
            <tr><td style="padding: 2px;"><strong>Accuracy:</strong></td><td>{}</td></tr>
            <tr><td style="padding: 2px;"><strong>Precision:</strong></td><td>{}</td></tr>
            <tr><td style="padding: 2px;"><strong>Recall:</strong></td><td>{}</td></tr>
            <tr><td style="padding: 2px;"><strong>F1 Score:</strong></td><td>{}</td></tr>
        </table>
        """.format(
            f"{obj.accuracy:.3f}" if obj.accuracy else "N/A",
            f"{obj.precision:.3f}" if obj.precision else "N/A",
            f"{obj.recall:.3f}" if obj.recall else "N/A",
            f"{obj.f1_score:.3f}" if obj.f1_score else "N/A"
        )
        return mark_safe(metrics_html)
    performance_metrics_display.short_description = 'Performance Metrics'
    
    def hyperparameters_display(self, obj):
        """Display hyperparameters in formatted JSON"""
        if not obj.hyperparameters:
            return "No hyperparameters configured"
        return format_html(
            '<pre style="background: #f8f9fa; padding: 10px; border-radius: 4px;">{}</pre>',
            json.dumps(obj.hyperparameters, indent=2)
        )
    hyperparameters_display.short_description = 'Hyperparameters'
    
    def feature_config_display(self, obj):
        """Display feature configuration in formatted JSON"""
        if not obj.feature_config:
            return "No feature configuration available"
        return format_html(
            '<pre style="background: #f8f9fa; padding: 10px; border-radius: 4px;">{}</pre>',
            json.dumps(obj.feature_config, indent=2)
        )
    feature_config_display.short_description = 'Feature Configuration'
    
    actions = ['mark_as_active', 'mark_as_deprecated']
    
    def mark_as_active(self, request, queryset):
        """Mark selected models as active"""
        updated = queryset.update(status='active')
        self.message_user(
            request,
            f'{updated} model(s) marked as active.',
            messages.SUCCESS
        )
    mark_as_active.short_description = "Mark selected models as active"
    
    def mark_as_deprecated(self, request, queryset):
        """Mark selected models as deprecated"""
        updated = queryset.update(status='deprecated')
        self.message_user(
            request,
            f'{updated} model(s) marked as deprecated.',
            messages.SUCCESS
        )
    mark_as_deprecated.short_description = "Mark selected models as deprecated"


@admin.register(FeatureExtractionLog)
class FeatureExtractionLogAdmin(admin.ModelAdmin):
    """
    Django Admin interface for Feature Extraction Log management
    """
    
    list_display = [
        'log_id', 'tenant', 'extraction_type', 'entity_id',
        'feature_count', 'processing_time_display', 'success_display', 'created_at'
    ]
    
    list_filter = [
        'extraction_type', 'success', 'created_at', 'tenant'
    ]
    
    search_fields = [
        'tenant__name', 'entity_id', 'error_message'
    ]
    
    readonly_fields = [
        'created_at', 'extracted_features_display'
    ]
    
    fieldsets = (
        ('Extraction Information', {
            'fields': ('tenant', 'extraction_type', 'entity_id')
        }),
        ('Results', {
            'fields': (
                'feature_count', 'processing_time', 'success', 'error_message'
            )
        }),
        ('Extracted Features', {
            'fields': ('extracted_features_display',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def log_id(self, obj):
        return f"Log #{obj.id}"
    log_id.short_description = 'Log ID'
    
    def processing_time_display(self, obj):
        """Display processing time with color coding"""
        if obj.processing_time < 1.0:
            color = '#28a745'  # Green for fast
        elif obj.processing_time < 5.0:
            color = '#ffc107'  # Yellow for medium
        else:
            color = '#dc3545'  # Red for slow
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.2f}s</span>',
            color,
            obj.processing_time
        )
    processing_time_display.short_description = 'Processing Time'
    
    def success_display(self, obj):
        """Display success status with icon"""
        if obj.success:
            return mark_safe('<span style="color: #28a745;">✓ Success</span>')
        else:
            return mark_safe('<span style="color: #dc3545;">✗ Failed</span>')
    success_display.short_description = 'Status'
    
    def extracted_features_display(self, obj):
        """Display extracted features in formatted JSON"""
        if not obj.extracted_features:
            return "No features extracted"
        return format_html(
            '<pre style="background: #f8f9fa; padding: 10px; border-radius: 4px; max-height: 400px; overflow-y: auto;">{}</pre>',
            json.dumps(obj.extracted_features, indent=2)
        )
    extracted_features_display.short_description = 'Extracted Features'


@admin.register(AIMatchingResult)
class AIMatchingResultAdmin(admin.ModelAdmin):
    """
    Django Admin interface for AI Matching Results management
    """
    
    list_display = [
        'match_id', 'tenant', 'job_id', 'candidate_id',
        'match_score_display', 'confidence_display', 'model_version', 'created_at'
    ]
    
    list_filter = [
        'tenant', 'model_version', 'created_at'
    ]
    
    search_fields = [
        'tenant__name', 'job_id', 'candidate_id'
    ]
    
    readonly_fields = [
        'created_at', 'updated_at', 'score_breakdown_display',
        'reasoning_display', 'feature_importance_display'
    ]
    
    fieldsets = (
        ('Match Information', {
            'fields': ('tenant', 'job_id', 'candidate_id', 'model_version')
        }),
        ('Scoring Results', {
            'fields': (
                'match_score', 'confidence', 
                'skills_score', 'experience_score', 'location_score', 'education_score',
                'score_breakdown_display'
            )
        }),
        ('AI Analysis', {
            'fields': ('reasoning_display', 'feature_importance_display'),
            'classes': ('collapse',)
        }),
        ('Feedback & Learning', {
            'fields': ('human_feedback', 'actual_outcome'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('ai_model', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def match_id(self, obj):
        return f"Match #{obj.id}"
    match_id.short_description = 'Match ID'
    
    def match_score_display(self, obj):
        """Display match score with color coding and progress bar"""
        score_percent = int(obj.match_score * 100)
        
        if obj.match_score >= 0.8:
            color = '#28a745'  # Green
            bg_color = '#d4edda'
        elif obj.match_score >= 0.6:
            color = '#ffc107'  # Yellow
            bg_color = '#fff3cd'
        else:
            color = '#dc3545'  # Red
            bg_color = '#f8d7da'
        
        return format_html(
            '<div style="background: {}; padding: 4px 8px; border-radius: 4px; color: {}; font-weight: bold; text-align: center;">{:.1%}</div>',
            bg_color, color, obj.match_score
        )
    match_score_display.short_description = 'Match Score'
    
    def confidence_display(self, obj):
        """Display confidence level"""
        return f"{obj.confidence:.1%}"
    confidence_display.short_description = 'Confidence'
    
    def score_breakdown_display(self, obj):
        """Display detailed score breakdown"""
        breakdown_html = """
        <table style="width: 100%; border-collapse: collapse;">
            <tr><td style="padding: 2px;"><strong>Skills:</strong></td><td>{:.2f}</td></tr>
            <tr><td style="padding: 2px;"><strong>Experience:</strong></td><td>{:.2f}</td></tr>
            <tr><td style="padding: 2px;"><strong>Location:</strong></td><td>{:.2f}</td></tr>
            <tr><td style="padding: 2px;"><strong>Education:</strong></td><td>{:.2f}</td></tr>
        </table>
        """.format(
            obj.skills_score, obj.experience_score, 
            obj.location_score, obj.education_score
        )
        return mark_safe(breakdown_html)
    score_breakdown_display.short_description = 'Score Breakdown'
    
    def reasoning_display(self, obj):
        """Display AI reasoning in formatted JSON"""
        if not obj.reasoning:
            return "No reasoning available"
        return format_html(
            '<pre style="background: #f8f9fa; padding: 10px; border-radius: 4px; max-height: 300px; overflow-y: auto;">{}</pre>',
            json.dumps(obj.reasoning, indent=2)
        )
    reasoning_display.short_description = 'AI Reasoning'
    
    def feature_importance_display(self, obj):
        """Display feature importance weights"""
        if not obj.feature_importance:
            return "No feature importance data"
        return format_html(
            '<pre style="background: #f8f9fa; padding: 10px; border-radius: 4px; max-height: 300px; overflow-y: auto;">{}</pre>',
            json.dumps(obj.feature_importance, indent=2)
        )
    feature_importance_display.short_description = 'Feature Importance'


@admin.register(ModelTrainingQueue)
class ModelTrainingQueueAdmin(admin.ModelAdmin):
    """
    Django Admin interface for Model Training Queue management
    """
    
    list_display = [
        'queue_id', 'tenant_name', 'training_type', 'status_display', 
        'progress_display', 'created_at', 'completed_at'
    ]
    
    list_filter = [
        'training_type', 'status', 'created_at'
    ]
    
    search_fields = [
        'tenant__name', 'current_step', 'error_message'
    ]
    
    readonly_fields = [
        'created_at', 'started_at', 'completed_at', 
        'training_config_display', 'result_metadata_display'
    ]
    
    fieldsets = (
        ('Queue Information', {
            'fields': ('tenant', 'training_type', 'status', 'ai_model')
        }),
    )  # <-- CLOSED HERE

    def queue_id(self, obj):
        return f"Queue #{obj.id}"
    queue_id.short_description = "Queue ID"
    
    def tenant_name(self, obj):
        return obj.tenant.name if obj.tenant else "Global"
    tenant_name.short_description = "Tenant"

    def status_display(self, obj):
        color = {
            "pending": "#ffc107",
            "running": "#007bff",
            "completed": "#28a745",
            "failed": "#dc3545"
        }.get(obj.status, "#6c757d")
        return format_html('<span style="color: {};">{}</span>', color, obj.status.title())
    status_display.short_description = "Status"

    def progress_display(self, obj):
        percent = int(obj.progress * 100) if hasattr(obj, "progress") else 0
        bar = f'<div style="background:#e9ecef;border-radius:4px;width:100px;position:relative;"><div style="width: {percent}px; background: #007bff; height: 10px; border-radius: 4px;"></div></div>'
        return format_html('{} {}%', bar, percent)
    progress_display.short_description = "Progress"

    def training_config_display(self, obj):
        if not obj.training_config:
            return "No config"
        return format_html(
            '<pre style="background: #f8f9fa; padding: 10px; border-radius: 4px;">{}</pre>',
            json.dumps(obj.training_config, indent=2)
        )
    training_config_display.short_description = "Training Config"

    def result_metadata_display(self, obj):
        if not obj.result_metadata:
            return "No metadata"
        return format_html(
            '<pre style="background: #f8f9fa; padding: 10px; border-radius: 4px;">{}</pre>',
            json.dumps(obj.result_metadata, indent=2)
        )
    result_metadata_display.short_description = "Result Metadata"