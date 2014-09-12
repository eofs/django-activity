from django.dispatch import Signal

action = Signal(providing_args=['handler', 'actor', 'action_object', 'target', 'is_global', 'timestamp'])

pre_fanout = Signal(providing_args=['action'])
post_fanout = Signal(providing_args=['action'])
