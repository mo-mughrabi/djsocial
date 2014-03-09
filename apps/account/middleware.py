__author__ = 'ahmed'

from social_auth.middleware import SocialAuthExceptionMiddleware
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from social_auth.exceptions import AuthCanceled

class SocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):
        if type(exception) == AuthCanceled:
            return redirect(reverse('account-error'))
        else:
            pass
