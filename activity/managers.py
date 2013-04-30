from collections import defaultdict

from django.db.models import Manager, Q, get_model
from django.db.models.query import QuerySet

from django.contrib.contenttypes.models import ContentType

class ActionQuerySet(QuerySet):
    def public(self, *args, **kwargs):
        """
        Return list of public actions
        """
        kwargs['public'] = True
        return self.filter(*args, **kwargs)

    def private(self, *args, **kwargs):
        """
        Return list of private actions
        """
        kwargs['public'] = False
        return self.filter(*args, **kwargs)

    def actor(self, obj, **kwargs):
        """
        Return list of actions where object is the actor
        """
        content_type = ContentType.objects.get_for_model(obj).pk
        return self.filter(actor_content_type=content_type,
                           actor_object_id=obj.pk,
                           **kwargs)

    def target(self, obj, **kwargs):
        """
        Return list of actions where object is the target
        """
        content_type = ContentType.objects.get_for_model(obj).pk
        return self.filter(target_content_type=content_type,
                           target_object_id=obj.pk,
                           **kwargs)

    def action_object(self, obj, **kwargs):
        """
        Return list of actions where object is the action object
        """
        content_type = ContentType.objects.get_for_model(obj).pk
        return self.filter(action_object_content_type=content_type,
                           action_object_object_id=obj.pk,
                           **kwargs)

    def user(self, user, **kwargs):
        """
        Return list of most recent actions by objects that the given user is following
        """

        # Base filter
        q = Q()
        # Base QueryString
        qs = self.public()

        actors_by_content_type = defaultdict(lambda: [])
        others_by_content_type = defaultdict(lambda: [])

        following = get_model('activity', 'Follow').objects.filter(user=user).values_list('content_type_id', 'object_id', 'actor_only')
        if not following:
            return qs.none()

        for content_type_id, object_id, actor_only in following.iterator():
            actors_by_content_type[content_type_id].append(object_id)
            if not actor_only:
                others_by_content_type[content_type_id].append(object_id)

        for content_type_id, object_ids in actors_by_content_type.iteritems():
            q = q | Q(
                actor_content_type=content_type_id,
                actor_object_id__in=object_ids,
            )
        for content_type_id, object_ids in others_by_content_type.iteritems():
            q = q | Q(
                target_content_type=content_type_id,
                target_object_id__in=object_ids,
            ) | Q(
                action_object_content_type=content_type_id,
                action_object_object_id__in=object_ids,
            )
        return qs.filter(q, **kwargs)


class ActionManager(Manager):
    """
    Manager for Action model
    """

    def get_query_set(self):
        return ActionQuerySet(self.model, using=self._db)

    def __getattr__(self, attr, *args):
        """
        Pass every method/attr acceess call to ActionQuerySet if
        it has requested element available.
        """
        try:
            return getattr(self.__class__, attr, *args)
        except AttributeError:
            return getattr(self.get_query_set(), attr, *args)

class FollowManager(Manager):
    """
    Manager for Follow model
    """

    def for_object(self, target):
        """
        Filter to a specific target
        """
        content_type = ContentType.objects.get_for_model(target).pk
        return self.filter(content_type=content_type, object_id=target.pk)

    def is_following(self, user, target):
        """
        Is user following the target?
        """
        if not user or user.is_anonymous():
            return False
        queryset = self.for_object(target)
        return queryset.filter(user=user).exists()

    def followers(self, actor):
        """
        Return list of users who are following the given actor
        """
        return [follow.user for follow in self.filter(
                content_type=ContentType.objects.get_for_model(actor),
            object_id=actor.pk).select_related('user')]

    def following(self, user, *models):
        """
        Return list of actors that the given user is following.
        You may restrict the search by giving list of models.
        e.g. following(user, User) returns list of users the user is following
        """

        queryset = self.filter(user=user)
        if len(models):
            queryset = queryset.filter(content_type__in=(
                ContentType.objects.get_for_model(model) for model in models)
            )
        return [follow.follow_object for follow in queryset.prefetch_related()]
