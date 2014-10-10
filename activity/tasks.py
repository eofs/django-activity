import itertools

from celery import task
from celery.utils.log import get_task_logger

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model


logger = get_task_logger('celery.task')


@task
def fanout_action(action_id):
    """
    Fan-out action to feeds. Usually called when writing an action.
    """
    from activity.models import Action, Follow, Stream

    User = get_user_model()
    logger.info('Populating feeds')

    try:
        action = Action.objects.get(pk=action_id)
    except Action.DoesNotExist:
        logger.warning('Action %d does not exists!' % action_id)
        return False

    if not action.public:
        logger.warning('Cannot fan-out private action!')
        return False

    if action.is_global:
        logger.info('This action is global. Populating all streams.')

        user_ids = User.objects.values_list('pk', flat=True)
        Stream.objects.fanout(action, user_ids)
        logger.info('Stream population completed')
    else:
        # Action is not global, populate followers' streams
        user_type = ContentType.objects.get_for_model(User)

        followers = Follow.objects.filter(
            content_type=user_type,
            object_id=action.actor.pk,
            actor_only=True).values_list('user__pk', flat=True)

        # Get extra targets from activity handler
        extra = action.action_handler.fanout_extra_targets(action)

        # Combine targets and remove duplicates
        targets = list(set(itertools.chain(followers, extra)))

        if len(targets):
            Stream.objects.fanout(action, targets)
            logger.info('Stream population completed')
        else:
            logger.info('No followers, skipping')

    return True
