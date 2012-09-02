from django.conf.urls import patterns, include, url
from testdjango.facebookgraph.views import add_user, show_all_users, show_user_info

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'testdjango.views.home', name='home'),
    # url(r'^testdjango/', include('testdjango.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    url(r'^add_user/$', add_user),
    url(r'^all_users/$', show_all_users),
    url(r'^users/([^/]+)/$', show_user_info),
)
