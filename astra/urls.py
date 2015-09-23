from django.conf.urls import patterns, url, include
from astra.views import AdminSearch, AccountSearch, AccountSoC


urlpatterns = patterns(
    '',
    url(r'api/v1/admins/?$', AdminSearch().run),
    url(r'api/v1/accounts/?$', AccountSearch().run),
    url(r'api/v1/soc/?$', AccountSoC().run),
)
