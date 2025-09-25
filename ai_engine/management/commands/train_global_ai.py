# ai_engine/management/commands/train_global_ai.py

from django.core.management.base import BaseCommand
import pandas as pd
from ai_engine.ml_models.global_ai import train_global_model

class Command(BaseCommand):
    help = 'Train global AI model for candidate fit'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='Path to training CSV file')

    def handle(self, *args, **options):
        csv_path = options['csv_path']
        df = pd.read_csv(csv_path)
        feature_cols = [c for c in df.columns if c not in {"fit_label"}]
        model = train_global_model(df[feature_cols], df["fit_label"])
        self.stdout.write(self.style.SUCCESS(
            f"Global model trained and saved. Features: {feature_cols}"
        ))
