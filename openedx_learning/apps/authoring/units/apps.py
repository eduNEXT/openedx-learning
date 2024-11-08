"""
Unit Django application initialization.
"""

from django.apps import AppConfig


class UnitsConfig(AppConfig):
    """
    Configuration for the units Django application.
    """

    name = "openedx_learning.apps.authoring.units"
    verbose_name = "Learning Core > Authoring > Units"
    default_auto_field = "django.db.models.BigAutoField"
    label = "oel_units"
