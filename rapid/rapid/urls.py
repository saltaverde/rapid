from django.conf.urls import patterns, include, url
from django.contrib import admin
from rapid.models import DataLayer, GeoView

urlpatterns = patterns('rapid.views',

    url(r'^admin/', include(admin.site.urls)),

    # TODO: remove or obfuscate this view for security when transitioning to production (BC 12-8-15)
    url(r'^rapid/tokens/$', 'getTokens'),

    # File uploading
    url(r'^rapid/upload/$', 'uploadPage'),
    url(r'^rapid/uploadFile/$', 'uploadFile'),

    # User authentication
    url(r'^rapid/$', 'user_login'),
    url(r'^rapid/register/$', 'register'),
    url(r'^rapid/login/$', 'user_login'),
    url(r'^rapid/logout/$', 'user_logout'),

    # Portal
    url(r'^rapid/portal/$', 'portal'),

    # TEST #
############# REST API calls ################
    url(r'^rapid/feature/$', 'features'),
    url(r'^rapid/layer/$', 'layers'),
    url(r'^rapid/geoview/$', 'geoviews'),

    # url(r'^rapid/geoview/(?P<geo_uid>[\w]+)/export/$', 'exportGeoView'),
    # url(r'^rapid/layer/(?P<layer_uid>[\w]+)/export/$', 'exportLayer'),

    url(r'^rapid/feature/(?P<feature_uid>[\w]+)/$', 'getFeature'),
    url(r'^rapid/layer/(?P<layer_uid>[\w]+)/$', 'getLayer'),
    url(r'^rapid/geoview/(?P<geo_uid>[\w]+)/$', 'getGeoview'),

    url(r'^rapid/import/(?P<layerId>[\w]+)/', 'featuresFromURL'),

    url(r'^rapid/geoview/addlayer/(?P<geo_uid>[\w]+)/(?P<layer_uid>[\w]+)/$', 'addLayerToGeoview'),
    url(r'^rapid/geoview/removelayer/(?P<geo_uid>[\w]+)/(?P<layer_uid>[\w]+)/$', 'removeLayerFromGeoview'),

    url(r'^rapid/geoview/(?P<geo_uid>[\w]+)/add/layer/(?P<layer_uid>[\w]+)/$', 'addLayerToGeoview'),
    url(r'^rapid/geoview/(?P<geo_uid>[\w]+)/remove/layer/(?P<layer_uid>[\w]+)/$', 'removeLayerFromGeoview'),

    url(r'^rapid/geoview/(?P<geo_uid>[\w]+)/add/owner/(?P<token_uid>[\w]+)/$', 'addGeoViewOwner'),
    url(r'^rapid/geoview/(?P<geo_uid>[\w]+)/add/editor/(?P<token_uid>[\w]+)/$', 'addGeoViewEditor'),
    url(r'^rapid/geoview/(?P<geo_uid>[\w]+)/add/viewer/(?P<token_uid>[\w]+)$', 'addGeoViewViewer'),
    url(r'^rapid/layer/(?P<layer_uid>[\w]+)/add/owner/(?P<token_uid>[\w]+)/$', 'addLayerOwner'),
    url(r'^rapid/layer/(?P<layer_uid>[\w]+)/add/editor/(?P<token_uid>[\w]+)/$', 'addLayerEditor'),
    url(r'^rapid/layer/(?P<layer_uid>[\w]+)/add/viewer/(?P<token_uid>[\w]+)$', 'addLayerViewer'),

    url(r'^rapid/geoview/(?P<geo_uid>[\w]+)/remove/owner/(?P<token_uid>[\w]+)/$', 'removeGeoViewOwner'),
    url(r'^rapid/geoview/(?P<geo_uid>[\w]+)/remove/editor/(?P<token_uid>[\w]+)/$', 'removeGeoViewEditor'),
    url(r'^rapid/geoview/(?P<geo_uid>[\w]+)/remove/viewer/(?P<token_uid>[\w]+)$', 'removeGeoViewViewer'),
    url(r'^rapid/layer/(?P<layer_uid>[\w]+)/remove/owner/(?P<token_uid>[\w]+)/$', 'removeLayerOwner'),
    url(r'^rapid/layer/(?P<layer_uid>[\w]+)/remove/editor/(?P<token_uid>[\w]+)/$', 'removeLayerEditor'),
    url(r'^rapid/layer/(?P<layer_uid>[\w]+)/remove/viewer/(?P<token_uid>[\w]+)$', 'removeLayerViewer'),
############################################
)
