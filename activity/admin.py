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
    list_display = ('user', 'action', 'get_created', 'get_handler')
    list_filter = ('action__handler',
                   'action__is_global',
                   'action__actor_content_type',
                   'action__action_object_content_type',
                   'action__target_content_type')
    search_fields = ('user__username',)

    def get_created(self, obj):
        return obj.action.created
    get_created.short_description = 'Created'
    get_created.admin_order_field = 'action__created'

    def get_handler(self, obj):
        return obj.action.handler
    get_handler.short_description = 'Handler'
    get_handler.admin_order_field = 'action__handler'

admin.site.register(Stream, StreamAdmin)


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'follow_object', 'content_type', 'actor_only')
    list_filter = ('actor_only', 'content_type')
    search_fields = ('user__username',)

admin.site.register(Follow, FollowAdmin)
