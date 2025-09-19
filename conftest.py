import os
import django
from pathlib import Path
import sys

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set the Django settings module (adjust if needed)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LearningPlatform.settings")

# Setup Django
django.setup()

print("✅ Django setup complete for test discovery")