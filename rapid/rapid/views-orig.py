from django.contrib.gis.geos import GEOSGeometry
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.static import serve
from .forms import UploadFileForm
from django.shortcuts import render_to_response, render
import os
from rest_framework.renderers import JSONRenderer
import urllib
import json
from rapid.importer import Importer
from rapid.select import *
from rapid.helpers import *


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def get_token_key(request):
    token_key = None
    if request.GET.get('token'):
        token_key = request.GET.get('token')
    elif request.POST.get('token'):
        token_key = request.POST.get('token')

    return token_key


@csrf_exempt
def layers(request):
    message = ''
    descriptor = None
    properties = None
    is_public = None

    token_key = get_token_key(request)
    data = DataOperator(token_key)

    if request.method == 'POST':
        jsonDict = json.loads(request.body)

        if 'des' in jsonDict:
            descriptor = jsonDict['des']

        if 'public' in jsonDict:
            if jsonDict['public'] == "False" or jsonDict['public'] == False:
                is_public = False
            else:
                is_public = True

        if 'props' in jsonDict:
            properties = jsonDict['props']

        uid = data.create_layer(descriptor, is_public, properties)

        role = DataLayerRole(layer_id=uid, token=data.get_apitoken(), role=Role.OWNER)
        role.save()

        message = to_json(uid)
        return HttpResponse(message)

    elif request.method == 'GET':
        all_layers = data.get_layers()
        all_layers = list(all_layers)

        layers = []

        for layer in all_layers:
            if data.has_layer_permissions(layer.uid, Role.VIEWER):
                layers.append(layer)

        for layer in layers:
            layer.include_features = False

        message = to_json(layers)

        for layer in layers:
            layer.include_features = True

    return HttpResponse(message)


@csrf_exempt
def geoviews(request):
    message = ''
    geometry = None
    descriptor = None
    properties = None
    public = False

    token_key = get_token_key(request)
    data = DataOperator(token_key)

    if request.method == 'POST':
        jsonDict = json.loads(request.body)

        if 'geom' in jsonDict:
            geometry = str(jsonDict['geom']).replace('u\'', '\'')
            geometry = GEOSGeometry(geometry)

        if 'des' in jsonDict:
            descriptor = jsonDict['des']

        if 'public' in jsonDict:
            if jsonDict['public'] == "False" or jsonDict['public'] == False:
                public = False
            else:
                public = True

        if 'props' in jsonDict:
            properties = jsonDict['props']

        uid = data.create_geoview(geometry, descriptor, properties, public)

        role = GeoViewRole(geo_view_id=uid, token=data.get_apitoken(), role=Role.OWNER)
        role.save()

        message = to_json(uid)
        return HttpResponse(message)

    elif request.method == 'GET':
        all_geoviews = data.get_geoviews()

        geoviews = []
        for geoview in all_geoviews:
            if data.has_geoview_permissions(geoview.uid, Role.VIEWER):
                geoviews.append(geoview)

        message = to_json(geoviews)

        return HttpResponse(message)
    return HttpResponse(message)

@csrf_exempt
def addGeoViewOwner(request, geo_uid, token_uid):
    token_key = get_token_key(request)
    data = DataOperator(token_key)

    if data.has_geoview_permissions(geo_uid, Role.OWNER):
        role = GeoViewRole(geo_view_id=geo_uid, role=Role.OWNER, token_id=token_uid)
        role.save()
        return HttpResponse(json_error('Added access for token.'))
    else:
        return HttpResponse(json_error('Not permitted to edit GeoView.'))

@csrf_exempt
def addGeoViewEditor(request, geo_uid, token_uid):
    token_key = get_token_key(request)
    data = DataOperator(token_key)

    if data.has_geoview_permissions(geo_uid, Role.OWNER):
        role = GeoViewRole(geo_view_id=geo_uid, role=Role.EDITOR, token_id=token_uid)
        role.save()
        return HttpResponse(json_error('Added access for token.'))
    else:
        return HttpResponse(json_error('Not permitted to edit GeoView.'))

@csrf_exempt
def addGeoViewViewer(request, geo_uid, token_uid):
    token_key = get_token_key(request)
    data = DataOperator(token_key)

    if data.has_geoview_permissions(geo_uid, Role.OWNER):
        role = GeoViewRole(geo_view_id=geo_uid, role=Role.VIEWER, token_id=token_uid)
        role.save()
        return HttpResponse(json_error('Added access for token.'))
    else:
        return HttpResponse(json_error('Not permitted to edit GeoView.'))

@csrf_exempt
def addLayerOwner(request, layer_uid, token_uid):
    token_key = get_token_key(request)
    data = DataOperator(token_key)

    if data.has_layer_permissions(layer_uid, Role.OWNER):
        role = GeoViewRole(layer_id=layer_uid, role=Role.OWNER, token_id=token_uid)
        role.save()
        return HttpResponse(json_error('Added access for token.'))
    else:
        return HttpResponse(json_error('Not permitted to edit layer.'))

@csrf_exempt
def addLayerEditor(request, layer_uid, token_uid):
    token_key = get_token_key(request)
    data = DataOperator(token_key)

    if data.has_layer_permissions(layer_uid, Role.OWNER):
        role = DataLayerRole(layer_id=layer_uid, role=Role.EDITOR, token_id=token_uid)
        role.save()
        return HttpResponse(json_error('Added access for token.'))
    else:
        return HttpResponse(json_error('Not permitted to edit layer.'))

@csrf_exempt
def addLayerViewer(request, layer_uid, token_uid):
    token_key = get_token_key(request)
    data = DataOperator(token_key)

    if data.has_layer_permissions(layer_uid, Role.OWNER):
        role = DataLayerRole(layer_id=layer_uid, role=Role.VIEWER, token_id=token_uid)
        role.save()
        return HttpResponse(json_error('Added access for token.'))
    else:
        return HttpResponse(json_error('Not permitted to edit layer.'))

@csrf_exempt
def removeGeoViewOwner(request, geo_uid, token_uid):
    token_key = get_token_key(request)
    data = DataOperator(token_key)

    if data.has_geoview_permissions(geo_uid, Role.OWNER):
        GeoViewRole.objects.filter(geo_view_id=geo_uid, role=Role.OWNER, token_id=token_uid).delete()
        return HttpResponse(json_error('Removed access for token.'))
    else:
        return HttpResponse(json_error('Not permitted to edit GeoView.'))

@csrf_exempt
def removeGeoViewEditor(request, geo_uid, token_uid):
    token_key = get_token_key(request)
    data = DataOperator(token_key)

    if data.has_geoview_permissions(geo_uid, Role.OWNER):
        GeoViewRole.objects.filter(geo_view_id=geo_uid, role=Role.EDITOR, token_id=token_uid).delete()
        return HttpResponse(json_error('Removed access for token.'))
    else:
        return HttpResponse(json_error('Not permitted to edit GeoView.'))

@csrf_exempt
def removeGeoViewViewer(request, geo_uid, token_uid):
    token_key = get_token_key(request)
    data = DataOperator(token_key)

    if data.has_geoview_permissions(geo_uid, Role.OWNER):
        GeoViewRole.objects.filter(geo_view_id=geo_uid, role=Role.VIEWER, token_id=token_uid).delete()
        return HttpResponse(json_error('Removed access for token.'))
    else:
        return HttpResponse(json_error('Not permitted to edit GeoView.'))

@csrf_exempt
def removeLayerOwner(request, layer_uid, token_uid):
    token_key = get_token_key(request)
    data = DataOperator(token_key)

    if data.has_layer_permissions(layer_uid, Role.OWNER):
        DataLayerRole.objects.filter(layer_id=layer_uid, role=Role.OWNER, token_id=token_uid).delete()
        return HttpResponse(json_error('Removed access for token.'))
    else:
        return HttpResponse(json_error('Not permitted to edit Layer.'))

@csrf_exempt
def removeLayerEditor(request, layer_uid, token_uid):
    token_key = get_token_key(request)
    data = DataOperator(token_key)

    if data.has_layer_permissions(layer_uid, Role.OWNER):
        DataLayerRole.objects.filter(layer_id=layer_uid, role=Role.EDITOR, token_id=token_uid).delete()
        return HttpResponse(json_error('Removed access for token.'))
    else:
        return HttpResponse(json_error('Not permitted to edit Layer.'))

@csrf_exempt
def removeLayerViewer(request, layer_uid, token_uid):
    token_key = get_token_key(request)
    data = DataOperator(token_key)

    if data.has_layer_permissions(layer_uid, Role.OWNER):
        DataLayerRole.objects.filter(layer_id=layer_uid, role=Role.VIEWER, token_id=token_uid).delete()
        return HttpResponse(json_error('Removed access for token.'))
    else:
        return HttpResponse(json_error('Not permitted to edit Layer.'))

@csrf_exempt
def addLayerToGeoview(request, geo_uid, layer_uid):
    token_key = get_token_key(request)
    data = DataOperator(token_key)

    if data.has_geoview_permissions(geo_uid, Role.EDITOR):
        message = data.add_layer_to_geoview(geo_uid, layer_uid)
        return HttpResponse(json_error(message))
    else:
        return HttpResponse(json_error('Not permitted to edit GeoView.'))

@csrf_exempt
def removeLayerFromGeoview(request, geo_uid, layer_uid):
    token_key = get_token_key(request)
    data = DataOperator(token_key)

    if data.has_geoview_permissions(geo_uid, Role.EDITOR):
        message = data.remove_layer_from_geoview(geo_uid, layer_uid)
        return HttpResponse(json_error(message))
    else:
        return HttpResponse(json_error('Not permitted to edit GeoView.'))

    return HttpResponse(json_error(message))

@csrf_exempt
def features(request):
    token_key = get_token_key(request)
    data = DataOperator(token_key)

    if request.method == 'POST':
        jsonDict = json.loads(request.body)
        if jsonDict['layer']:
            layer = jsonDict['layer']
            layer = data.get_layer(layer)

            if not data.has_layer_permissions(layer.uid, Role.EDITOR):
                return HttpResponse(json_error('No editing permissions on Layer.'))
        if jsonDict['content']:
            content = jsonDict['content']
            if content['geom']:
                geom = content['geom']
        if jsonDict['props']:
            properties = jsonDict['props']
        # archive = create_archive(content, layer, models.FileType.GEOJSON, token)
        feature = data.create_feature(geom, layer, properties=properties)
        myjson = to_json(feature)
        return HttpResponse(myjson, content_type='application/json')
    return HttpResponse(json_error('Must POST a feature to this endpoint'))

@csrf_exempt
def featuresFromURL(request, layerId):
    token_key = get_token_key(request)
    data = DataOperator(token_key)
    importer = Importer(token_key)

    if not data.has_layer_permissions(layerId, Role.EDITOR):
        return HttpResponse(json_error('No editing permissions on layer.'))

    if request.method == 'GET':
        if request.GET.get('url'):
            try:
                url = request.GET.get('url')
                url=urllib.unquote(url).decode('utf8')
                importer.import_geojson_url(url, layerId)
                return HttpResponse(json_error('Imported GeoJSON into layer.'))
            except:
                return HttpResponse(json_error('Unable to import GeoJSON to layer.'))
        return HttpResponse(json_error('Must include GeoJSON URL to import.'))
    return HttpResponse(json_error('must GET'))

@csrf_exempt
def getFeature(request, feature_uid):
    token_key = get_token_key(request)
    data = DataOperator(token_key)

    if request.method == 'POST':
        jsonDict = json.loads(request.body)
        if jsonDict['layer']:
            layer = jsonDict['layer']
            layer = data.get_layer(layer)

            if not data.has_layer_permissions(layer.uid, Role.EDITOR):
                return HttpResponse(json_error('No editing permissions on Layer.'))
        if jsonDict['content']:
            content = jsonDict['content']
            if content['geom']:
                geom = content['geom']
        if jsonDict['props']:
            properties = jsonDict['props']
        archive = None
        feature = data.update_feature(feature_uid, geom, layer, archive, properties)
        myjson = to_json(feature)
        return HttpResponse(myjson, content_type='application/json')
    if request.method == 'GET':
        feature = data.get_feature(feature_uid)

        if not data.has_layer_permissions(feature.layer.uid, Role.VIEWER):
            return HttpResponse('No viewing permissions for Feature.')

        myjson = to_json(feature)
        return HttpResponse(myjson, content_type='application/json')
    if request.method == 'DELETE':
        feature = data.get_feature(feature_uid)

        if not data.has_layer_permissions(feature.layer.uid, Role.EDITOR):
            return HttpResponse('No editing permissions for Feature.')

        data.delete_feature(feature_uid)
        message = "DELETE layer with uid ", feature_uid
        return HttpResponse(json_error(message))
    return HttpResponse(json_error('ERROR: must POST, GET, or DELETE'))


@csrf_exempt
def getLayer(request, layer_uid):
    token_key = get_token_key(request)
    data = DataOperator(token_key)

    if request.method == 'GET':
        start = None
        stop = None
        if request.GET.get('start'):
            start = float(request.GET.get('start'))
        if request.GET.get('stop'):
            stop = float(request.GET.get('stop'))
            #layer = layer.features.filter
        layer = data.get_layer(layer_uid)

        if not data.has_layer_permissions(layer_uid, Role.VIEWER):
            return HttpResponse(json_error('No viewing permissions for this layer.'))

        layer.include_features = True
        myjson = to_json(layer)
        layer.include_features = False

        return HttpResponse(myjson, content_type='application/json')
    if request.method == 'DELETE':
        if not data.has_layer_permissions(layer_uid, Role.EDITOR):
            return HttpResponse(json_error('No editing permissions for this layer.'))
        data.delete_layer(layer_uid)
        message = "DELETE layer with uid ", layer_uid, " :: SUCCESS"
        return HttpResponse(json_error(message))
    return HttpResponse(json_error('ERROR: must GET or DELETE'))

@csrf_exempt
def getTokens(request):
    json_resp = to_json(DataOperator().get_apitokens())
    return HttpResponse(json_resp)


@csrf_exempt
def getGeoview(request, geo_uid):
    token_key = get_token_key(request)
    data = DataOperator(token_key)

    if request.method == 'GET':
        if not data.has_geoview_permissions(geo_uid, Role.VIEWER):
            return HttpResponse(json_error('No viewing permissions for this GeoView.'))

        file = False
        if request.GET.get('file'):
            filepath = data.get_geoview(geo_uid, file)
            return serve(request, os.path.basename(filepath), os.path.dirname(filepath))
        else:
            geoview = data.get_geoview(geo_uid)
            geoview.include_layers = geoview.include_geom = True
            geoview.token_key = token_key
            myjson = to_json(geoview)
            geoview.include_layers = geoview.include_geom = False
            return HttpResponse(myjson, content_type='application/json')
    if request.method == 'DELETE':
        if not data.has_geoview_permissions(geo_uid, Role.EDITOR):
            return HttpResponse(json_error('No editing permissions for this GeoView.'))
        data.delete_geoview(geo_uid)
        message = "Deleted GeoView with uid " + str(geo_uid)
        return HttpResponse(json_error(message))
    return HttpResponse(json_error('ERROR: must GET or DELETE GeoViews'))

@csrf_exempt
def uploadPage(request):
    form = UploadFileForm()
    context = {'form':form}
    return render(request, 'upload/uploadform.html', context)

@csrf_exempt
def uploadFile(request, file_name):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            #return HttpResponseRedirect('/success/url/')
    else:
        form = UploadFileForm()
    return render_to_response('upload.html', {'form': form})

@csrf_exempt
def handle_uploaded_file(f, file_name):
    with open('/data/dropbox/' + file_name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
