# ai_engine/management/commands/retrain_tenant_ai.py

from django.core.management.base import BaseCommand
import pandas as pd
from ai_engine.ml_models.tenant_ai import train_tenant_model
from core.models import Tenant

class Command(BaseCommand):
    help = 'Retrain AI model for a specific tenant'

    def add_arguments(self, parser):
        parser.add_argument('tenant_id', type=int, help='Tenant ID')
        parser.add_argument('csv_path', type=str, help='Path to tenant training CSV file')

    def handle(self, *args, **options):
        tenant_id = options['tenant_id']
        csv_path = options['csv_path']
        df = pd.read_csv(csv_path)
        feature_cols = [c for c in df.columns if c not in {"fit_label"}]
        model = train_tenant_model(tenant_id, df[feature_cols], df["fit_label"])
        self.stdout.write(self.style.SUCCESS(
            f"Tenant {tenant_id} model retrained and saved. Features: {feature_cols}"
        ))
