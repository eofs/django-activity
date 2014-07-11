from celery import task
from celery.utils.log import get_task_logger

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

from activity.models import Action, Follow, Stream


logger = get_task_logger('celery.task')


@task
def fanout_action(action_id):
    """
    Fan-out action to feeds. Usually called when writing an action.
    """

    logger.info('Populating feeds')
    try:
        action = Action.objects.get(pk=action_id)
    except Action.DoesNowExists:
        logger.warning('Action %d does not exists!' % action_id)
        return False

    if not action.public:
        logger.warning('Cannot fan-out private action!')
        return False

    User = get_user_model()
    user_type = ContentType.objects.get_for_model(User)

    followers = Follow.objects.filter(
        content_type=user_type,
        object_id=action.actor.pk,
        actor_only=True).values_list('user__pk')
    followers_ids, = zip(*followers)

    Stream.objects.fanout(action, followers_ids)
    logger.info('Stream population completed')
