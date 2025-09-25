# ai_engine/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import Tenant  # Adjust if Tenant is elsewhere
from ai_engine.ml_models.tenant_ai import clone_global_model_for_tenant
from ai_engine.models import AIModelMetadata

@receiver(post_save, sender=Tenant)
def initialize_tenant_ai_model(sender, instance, created, **kwargs):
    """
    On tenant creation, clone the global AI model for the tenant
    and register a new AIModelMetadata entry.
    """
    if created:
        # Clone the global AI model for tenant (creates a new pkl file)
        model_path = clone_global_model_for_tenant(instance.id)
        # Create metadata entry for the new tenant model
        AIModelMetadata.objects.create(
            tenant=instance,
            model_type="tenant",
            model_path=model_path,
            version="1.0.0",
            status="active",  # or "training" if you trigger async retrain
        )
