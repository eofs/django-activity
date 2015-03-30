from django.template.loader import render_to_string
from django.utils.timesince import timesince as _timesince
from django.utils.translation import ugettext as _


class AlreadyRegistered(Exception):
    pass


class ActionHandler(object):
    template_name = 'activity/item.html'
    verb = 'created'

    def render(self, item):
        context = self.get_context_data(item)
        return render_to_string(self.template_name, context)

    def get_context_data(self, item):
        return {
            'actor': item.actor,
            'target': item.target,
            'verb': _(self.verb),
            'since': self.timesince(item.created),
            'activity': item
        }

    def timesince(self, time, now=None):
        """
        Shortcut for ``django.utils.timesince.timesince`` function
        """
        return _timesince(time, now)

    def fanout_extra_targets(self, item):
        """
        Extra targets to use in fan-out operation. Returned values are merged
        into target list created using Follow-objects.
        """
        return []


class ActivityRegistry(object):
    handlers = {}

    def register(self, id, handler_class=ActionHandler, **options):
        if id in self.handlers:
            id = self.handlers[id].id
            raise AlreadyRegistered('%r is already registered' % id)

        self.handlers[id] = handler_class()

    def autodiscover(self):
        from importlib import import_module
        from django.conf import settings

        for app in settings.INSTALLED_APPS:
            try:
                import_module('%s.activity_registry' % app)
            except ImportError:
                pass

    def get_handlers(self):
        return self.handlers


activityregistry = ActivityRegistry()
