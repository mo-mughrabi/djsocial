# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls import patterns, url, include
from views import Signup, Logout, Verify, SocialRegister, Profile, DeleteProfileView

urlpatterns = patterns('',
                       url(r'^sign-up/$', Signup.as_view(), name='account-signup'),
                       url(r'^logout/$', Logout.as_view(), name='account-logout'),
                       url(r'^profile/$', Profile.as_view(), name='account-profile'),
                       url(r'^verify/(?P<verification_code>[-\w]+)/$', Verify.as_view(), name='account-verify'),
                       url(r'^social-register/$', SocialRegister.as_view(), name='account-social-register'),
                       url(r'^delete-user/(?P<pk>[-\w]+)/$', DeleteProfileView.as_view(), name='account-delete-user'),
)

urlpatterns += patterns('',
                        url(r'', include('social_auth.urls'))
)