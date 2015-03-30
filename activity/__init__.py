from django.utils.module_loading import autodiscover_modules

__version__ = '0.4.0'

try:
    from activity.signals import action
except ImportError:
    pass


def autodiscover():
    autodiscover_modules('activity_registry')