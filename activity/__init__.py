__version__ = '0.4.0'

try:
    from activity.signals import action
except ImportError:
    pass
