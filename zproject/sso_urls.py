from django.conf.urls import url
import zerver.views.auth

urlpatterns = [
    url(r'^accounts/login/sso/$', zerver.views.auth.remote_user_sso, name='login-sso'),
]
