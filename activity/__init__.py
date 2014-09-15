__version__ = '0.2.2'

try:
    from activity.signals import action
except ImportError:
    pass
