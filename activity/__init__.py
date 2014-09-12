__version__ = '0.1.3'

try:
    from activity.signals import action
except ImportError:
    pass
