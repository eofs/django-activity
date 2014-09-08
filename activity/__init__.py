__version__ = '0.1.2'

try:
    from activity.signals import action
except ImportError:
    pass
