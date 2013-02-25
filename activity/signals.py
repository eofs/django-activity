from django.dispatch import Signal

action = Signal(providing_args=['handler', 'actor', 'action_object', 'target', 'timestamp'])
