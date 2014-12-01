from django.conf import settings
from django.db import models, connection
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.utils.timesince import timesince as _timesince
from django.utils.translation import ugettext as _

from activity.registry import activityregistry
from activity.signals import action
from activity.managers import ActionManager, FollowManager, StreamManager
from activity.tasks import fanout_action


class Action(models.Model):
    """
    Action model is used to describe the event.

    Naming convention from http://activitystrea.ms/specs/atom/1.0/
    """
    handler = models.CharField(max_length=255)

    actor_content_type = models.ForeignKey(ContentType, related_name='actor')
    actor_object_id = models.PositiveIntegerField()
    actor = generic.GenericForeignKey('actor_content_type', 'actor_object_id')

    action_object_content_type = models.ForeignKey(ContentType, related_name='action_object', blank=True, null=True)
    action_object_object_id = models.CharField(max_length=255, blank=True, null=True)
    action_object = generic.GenericForeignKey('action_object_content_type', 'action_object_object_id')

    target_content_type = models.ForeignKey(ContentType, related_name='target', blank=True, null=True)
    target_object_id = models.CharField(max_length=255, blank=True, null=True)
    target = generic.GenericForeignKey('target_content_type', 'target_object_id')

    created = models.DateTimeField(auto_now_add=True)
    public = models.BooleanField(default=True)
    is_global = models.BooleanField(default=False)

    objects = ActionManager()

    class Meta:
        ordering = ('-created',)

    def __unicode__(self):
        values = {
            'actor': self.actor,
            'verb': self.verb,
            'action_object': self.action_object,
            'target': self.target,
            'since': self.timesince()
        }
        if self.target:
            if self.action_object:
                return _('%(actor)s %(verb)s %(action_object)s on %(target)s %(since)s ago') % values
            else:
                return _('%(actor)s %(verb)s %(target)s %(since)s ago') % values
        if self.action_object:
            return _('%(actor)s %(verb)s %(action_object)s %(since)s ago') % values
        return _('%(actor)s %(verb)s %(since)s ago') % values

    @property
    def action_handler(self):
        """
        Get action handler object
        """
        handlers = activityregistry.get_handlers()
        return handlers[self.handler]

    @property
    def verb(self):
        """
        Get action's verb
        """
        return self.action_handler.verb

    def timesince(self, now=None):
        """
        Shortcut for ``django.utils.timesince.timesince`` function
        """
        return _timesince(self.created, now)


class Stream(models.Model):
    """
    User's activity stream item. This is used to pre-populate activity streams
    and to avoid scans on Action table.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    action = models.ForeignKey(Action)

    objects = StreamManager()

    class Meta:
        unique_together = ('user', 'action')


class Follow(models.Model):
    """
    Let user to follow activities of any user or object
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    # Object to Follow
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    follow_object = generic.GenericForeignKey()
    actor_only = models.BooleanField('Only follow actions where the object is the actor', default=True)

    started = models.DateTimeField(auto_now_add=True)

    objects = FollowManager()

    class Meta:
        # User can follow an object only once
        unique_together = ('user', 'content_type', 'object_id')

    def __unicode__(self):
        return u'%s follows %s' % (self.user, self.follow_object)


@receiver(post_save, sender=Action)
def action_post_save_fanout(sender, instance, created, **kwargs):
    """
    Fanout action if new instance saved
    """
    if created:
        # Fanout action (populate streams)
        if hasattr(connection, 'on_commit'):
            # Use django-transaction-hook to trigger tasks after transaction commit
            connection.on_commit(lambda: fanout_action.delay(instance.pk))
        else:
            fanout_action.delay(instance.pk)


def action_handler(sender, **kwargs):
    handlers = activityregistry.get_handlers()
    handler_name = kwargs.get('handler')
    actor = kwargs.get('actor')
    is_global = kwargs.get('is_global', False)
    if handler_name in handlers:
        action = Action(
            handler=handler_name,
            actor_content_type=ContentType.objects.get_for_model(actor),
            actor_object_id=actor.pk,
            is_global=is_global,
        )
        for opt in ('action_object', 'target'):
            obj = kwargs.get(opt, None)
            if obj is not None:
                setattr(action, '%s_object_id' % opt, obj.pk)
                setattr(action, '%s_content_type' % opt,
                        ContentType.objects.get_for_model(obj))
        action.save()


action.connect(action_handler, dispatch_uid='activity.models')
