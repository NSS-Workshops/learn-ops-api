from django.apps import AppConfig

class LearningAPIConfig(AppConfig):
    name = 'LearningAPI'

    def ready(self):
        import LearningAPI.signals  # noqa: F401
