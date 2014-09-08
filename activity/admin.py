from django.contrib import admin

from activity.models import Action, Follow, Stream


class ActionAdmin(admin.ModelAdmin):
    list_display = ('handler',
                    'actor_content_type', 'actor',
                    'verb',
                    'action_object_content_type', 'action_object',
                    'target_content_type', 'target',
                    'is_global',)
    list_filter = ('handler',
                   'actor_content_type',
                   'action_object_content_type',
                   'target_content_type',
                   'is_global',)

admin.site.register(Action, ActionAdmin)


class StreamAdmin(admin.ModelAdmin):
    list_display = ('user', 'action')

admin.site.register(Stream, StreamAdmin)


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'follow_object', 'content_type', 'actor_only')
    list_filter = ('actor_only', 'content_type')
    search_fields = ('user__username',)

admin.site.register(Follow, FollowAdmin)
