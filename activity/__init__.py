__version__ = '0.1.1'

try:
    from activity.signals import action
except ImportError:
    pass
