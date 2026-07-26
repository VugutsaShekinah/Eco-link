from django.apps import AppConfig


class DropoffsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dropoffs"

    def ready(self):
        # Connect the post_save signal handler when the app loads.
        from . import signals  # noqa: F401
