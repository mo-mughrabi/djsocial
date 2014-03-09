# -*- coding: utf-8 -*-
from django.contrib import admin
from models import Twitter, ScheduleOrder, Order

class TwitterAdmin(admin.ModelAdmin):
    list_display = ('user', 'tid', 'screen_name','followers_sum', 'following_sum')

# Now register the new TwitterAdmin...
admin.site.register(Twitter, TwitterAdmin)

class ScheduleOrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'label', 'status','created_at', 'last_run')

admin.site.register(ScheduleOrder, ScheduleOrderAdmin)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'schedule_order', 'status','created_at', 'executed_at')

admin.site.register(Order, OrderAdmin)