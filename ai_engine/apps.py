from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class AiEngineConfig(AppConfig):
    """
    Django app configuration for AI Engine
    Handles AI model initialization and signal registration
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_engine'
    verbose_name = 'AI Engine'
    
    def ready(self):
        """
        Initialize AI engine when Django starts
        Register signals for automatic tenant AI model creation
        """
        try:
            # Import signals to register them
            from . import signals
            
            # Initialize global AI model directory
            self._ensure_model_directories()
            
            logger.info("AI Engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI Engine: {e}")
    
    def _ensure_model_directories(self):
        """
        Create necessary directories for AI model storage
        """
        import os
        from django.conf import settings
        
        # Create model storage directories
        model_dirs = [
            os.path.join(settings.BASE_DIR, 'models', 'global'),
            os.path.join(settings.BASE_DIR, 'models', 'tenants'),
            os.path.join(settings.BASE_DIR, 'media', 'resumes'),
        ]
        
        for directory in model_dirs:
            os.makedirs(directory, exist_ok=True)
            
        logger.info("AI model directories created successfully")