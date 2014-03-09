# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth.admin import UserAdmin
from forms import UserChangeForm, UserCreationForm
from models import User

class UserAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password'), 'classes': ('suit-tab suit-tab-general', )}),
        (_('Personal info'), {
            'fields': ('full_name', 'email', 'gender', 'threshold' ),
            'classes': ('suit-tab suit-tab-general', )
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('suit-tab suit-tab-general', )
        }),
        (_('Important dates'), {
            'fields': ('last_login', ),
            'classes': ('suit-tab suit-tab-general', )
        }),
        )
    suit_form_tabs = (('general', 'General'),)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2')}
            ),
        )

    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    list_display = ('username', 'email', 'full_name','is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'full_name', 'email')
    ordering = ('username',)
    list_filter = ('is_staff', 'is_superuser')

# Now register the new UserAdmin...
admin.site.register(User, UserAdmin)