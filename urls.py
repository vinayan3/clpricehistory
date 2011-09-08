from django.conf.urls.defaults import *
import price_tracker.views

from django.contrib import admin
admin.autodiscover()

handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = patterns(
    '',
    (r'^admin/', include(admin.site.urls)),
    (r'results', price_tracker.views.results),
    (r'^$', price_tracker.views.index)
#    ('^$', 'django.views.generic.simple.direct_to_template',
#     {'template': 'home.html'}),
)
