from activity.models import Action
from activity.registry import activityregistry

class ActivitiesView(object):
    def render(self, item):
        """
        Render activities recursively
        """
        if not isinstance(item, Action):
            output = []
            for value in item:
                output.append(self.render(value))
            return output
        else:
            try:
                handlers = activityregistry.get_handlers()
                return handlers[item.handler].render(item)
            except KeyError:
                from django.conf import settings
                if settings.DEBUG:
                    return 'No handler available for %s' % item.handler
                return ''

    def public(self, public=True, limit=10, render=True):
        """
        Get public activities
        """
        if public:
            result = Action.objects.public()[:limit]
        else:
            result = Action.objects.private()[:limit]
        if render:
            return self.render(result)
        return result

    def private(self, public=False, limit=10, render=True):
        """
        Get private activities
        """
        return self.public(public, limit, render)

    def user(self, user, limit=10, render=True):
        """
        Get actions from objects that the given user is following
        """
        result = Action.objects.user(user)[:limit]
        if render:
            return self.render(result)
        return result

activities = ActivitiesView()
