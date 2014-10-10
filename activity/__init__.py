__version__ = '0.3.0'

try:
    from activity.signals import action
except ImportError:
    pass
