# ai_engine/management/commands/validate_models.py

from django.core.management.base import BaseCommand
from ai_engine.ml_models.global_ai import load_global_model
from ai_engine.ml_models.tenant_ai import load_tenant_model
from ai_engine.utils.model_validation import is_model_file_valid
from core.models import Tenant

class Command(BaseCommand):
    help = 'Validate trained global and tenant models'

    def handle(self, *args, **options):
        ok = is_model_file_valid("models/global/global_ai_model.pkl", load_global_model)
        self.stdout.write(
            self.style.SUCCESS("Global model valid") if ok else self.style.ERROR("Global model NOT valid")
        )
        for tenant in Tenant.objects.all():
            ok = is_model_file_valid(f"models/tenants/tenant_{tenant.id}_ai_model.pkl", load_tenant_model)
            self.stdout.write(
                self.style.SUCCESS(f"Tenant {tenant.id} model valid")
                if ok else self.style.ERROR(f"Tenant {tenant.id} model NOT valid")
            )
