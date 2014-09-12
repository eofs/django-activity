__version__ = '0.2.0'

try:
    from activity.signals import action
except ImportError:
    pass
