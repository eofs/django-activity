from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.utils.translation import ugettext as _

from activity.compat import User
from activity.registry import activityregistry
from activity.signals import action
from activity.managers import ActionManager, FollowManager


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

    objects = ActionManager()

    class Meta:
        ordering = ('-created',)

    def __unicode__(self):
        values = {
            'actor': self.actor,
            'handler': self.handler,
            'target': self.target,
            'since': self.timesince()
        }
        return _('%(handler)s by %(actor)s, %(target)s [%(since)s ago]') % values

    def timesince(self, now=None):
        """
        Shortcut for ``django.utils.timesince.timesince`` function
        """
        from django.utils.timesince import timesince as _timesince
        return _timesince(self.created, now)

class Follow(models.Model):
    """
    Let user to follow activities of any user or object
    """
    user = models.ForeignKey(User)

    # Object to Follow
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    follow_object = generic.GenericForeignKey()
    actor_only = models.BooleanField('Only follow actions where the object is the target', default=True)

    started = models.DateTimeField(auto_now_add=True)

    objects = FollowManager()

    class Meta:
        # User can follow an object only once
        unique_together = ('user', 'content_type', 'object_id')

    def __unicode__(self):
        return u'%s follows %s' % (self.user, self.follow_object)


def action_handler(sender, **kwargs):
    handlers = activityregistry.get_handlers()
    handler_name = kwargs.get('handler')
    actor = kwargs.get('actor')
    if handler_name in handlers:
        action = Action(
            handler=handler_name,
            actor_content_type=ContentType.objects.get_for_model(actor),
            actor_object_id=actor.pk,
        )
        for opt in ('action_object', 'target'):
            obj = kwargs.get(opt, None)
            if obj is not None:
                setattr(action, '%s_object_id' % opt, obj.pk)
                setattr(action, '%s_content_type' % opt,
                        ContentType.objects.get_for_model(obj))
        action.save()


action.connect(action_handler, dispatch_uid='activity.models')
