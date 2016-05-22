from django.contrib.gis.geos import GEOSGeometry
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.static import serve
from django.template import RequestContext
import os
from rapid.models import *
from rapid.forms import UploadFileForm, UserForm, UserProfileForm
from django.shortcuts import render_to_response, render
from rest_framework.renderers import JSONRenderer
import urllib
import json
from rapid.importer import Importer
from rapid.select import *
from rapid.helpers import *
from django.contrib.auth.decorators import login_required
from rapid.settings import STATIC_URL, BASE_URL, FEATURETYPE_XML_TEMPLATE_PATH, GEOSERVER_REST_ENDPOINT
from rapid.geofence import *


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

def get_token_key(request):
    """
    Returns the API token key (not uid) by way of the uid stored in the
    Django request.session object
    """

    token_key = ApiToken.objects.get(uid=request.session.get('token')).key

    return token_key


@csrf_exempt
@login_required
def layers(request):
    message = ''
    descriptor = None
    properties = None
    is_public = None

    user_token_key = get_token_key(request)

    data = DataOperator(user_token_key)

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
@login_required
def geoviews(request):
    message = ''
    geometry = None
    descriptor = None
    properties = None
    public = False

    user_token_key = get_token_key(request)

    data = DataOperator(user_token_key)

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
@login_required
def addGeoViewOwner(request, geo_uid, token_uid):
    user_token_key = get_token_key(request)
    data = DataOperator(user_token_key)

    if data.has_geoview_permissions(geo_uid, Role.OWNER):
        role = GeoViewRole(geo_view_id=geo_uid, role=Role.OWNER, token_id=token_uid)
        role.save()
        return HttpResponse(json_error('Added access for token.'))
    else:
        return HttpResponse(json_error('Not permitted to edit GeoView.'))

@csrf_exempt
@login_required
def addGeoViewEditor(request, geo_uid, token_uid):
    user_token_key = get_token_key(request)
    data = DataOperator(user_token_key)

    if data.has_geoview_permissions(geo_uid, Role.OWNER):
        role = GeoViewRole(geo_view_id=geo_uid, role=Role.EDITOR, token_id=token_uid)
        role.save()
        return HttpResponse(json_error('Added access for token.'))
    else:
        return HttpResponse(json_error('Not permitted to edit GeoView.'))

@csrf_exempt
@login_required
def addGeoViewViewer(request, geo_uid, token_uid):
    user_token_key = get_token_key(request)
    data = DataOperator(user_token_key)

    if data.has_geoview_permissions(geo_uid, Role.OWNER):
        role = GeoViewRole(geo_view_id=geo_uid, role=Role.VIEWER, token_id=token_uid)
        role.save()
        return HttpResponse(json_error('Added access for token.'))
    else:
        return HttpResponse(json_error('Not permitted to edit GeoView.'))

@csrf_exempt
@login_required
def addLayerOwner(request, layer_uid, token_uid):
    user_token_key = get_token_key(request)
    data = DataOperator(user_token_key)

    if data.has_layer_permissions(layer_uid, Role.OWNER):
        role = GeoViewRole(layer_id=layer_uid, role=Role.OWNER, token_id=token_uid)
        role.save()
        return HttpResponse(json_error('Added access for token.'))
    else:
        return HttpResponse(json_error('Not permitted to edit layer.'))

@csrf_exempt
@login_required
def addLayerEditor(request, layer_uid, token_uid):
    user_token_key = get_token_key(request)
    data = DataOperator(user_token_key)

    if data.has_layer_permissions(layer_uid, Role.OWNER):
        role = DataLayerRole(layer_id=layer_uid, role=Role.EDITOR, token_id=token_uid)
        role.save()
        return HttpResponse(json_error('Added access for token.'))
    else:
        return HttpResponse(json_error('Not permitted to edit layer.'))

@csrf_exempt
@login_required
def addLayerViewer(request, layer_uid, token_uid):
    user_token_key = get_token_key(request)
    data = DataOperator(user_token_key)

    if data.has_layer_permissions(layer_uid, Role.OWNER):
        role = DataLayerRole(layer_id=layer_uid, role=Role.VIEWER, token_id=token_uid)
        role.save()
        return HttpResponse(json_error('Added access for token.'))
    else:
        return HttpResponse(json_error('Not permitted to edit layer.'))

@csrf_exempt
@login_required
def removeGeoViewOwner(request, geo_uid, token_uid):
    user_token_key = get_token_key(request)
    data = DataOperator(user_token_key)

    if data.has_geoview_permissions(geo_uid, Role.OWNER):
        GeoViewRole.objects.filter(geo_view_id=geo_uid, role=Role.OWNER, token_id=token_uid).delete()
        return HttpResponse(json_error('Removed access for token.'))
    else:
        return HttpResponse(json_error('Not permitted to edit GeoView.'))

@csrf_exempt
@login_required
def removeGeoViewEditor(request, geo_uid, token_uid):
    user_token_key = get_token_key(request)
    data = DataOperator(user_token_key)

    if data.has_geoview_permissions(geo_uid, Role.OWNER):
        GeoViewRole.objects.filter(geo_view_id=geo_uid, role=Role.EDITOR, token_id=token_uid).delete()
        return HttpResponse(json_error('Removed access for token.'))
    else:
        return HttpResponse(json_error('Not permitted to edit GeoView.'))

@csrf_exempt
@login_required
def removeGeoViewViewer(request, geo_uid, token_uid):
    user_token_key = get_token_key(request)
    data = DataOperator(user_token_key)

    if data.has_geoview_permissions(geo_uid, Role.OWNER):
        GeoViewRole.objects.filter(geo_view_id=geo_uid, role=Role.VIEWER, token_id=token_uid).delete()
        return HttpResponse(json_error('Removed access for token.'))
    else:
        return HttpResponse(json_error('Not permitted to edit GeoView.'))

@csrf_exempt
@login_required
def removeLayerOwner(request, layer_uid, token_uid):
    user_token_key = get_token_key(request)
    data = DataOperator(user_token_key)

    if data.has_layer_permissions(layer_uid, Role.OWNER):
        DataLayerRole.objects.filter(layer_id=layer_uid, role=Role.OWNER, token_id=token_uid).delete()
        return HttpResponse(json_error('Removed access for token.'))
    else:
        return HttpResponse(json_error('Not permitted to edit Layer.'))

@csrf_exempt
@login_required
def removeLayerEditor(request, layer_uid, token_uid):
    user_token_key = get_token_key(request)
    data = DataOperator(user_token_key)

    if data.has_layer_permissions(layer_uid, Role.OWNER):
        DataLayerRole.objects.filter(layer_id=layer_uid, role=Role.EDITOR, token_id=token_uid).delete()
        return HttpResponse(json_error('Removed access for token.'))
    else:
        return HttpResponse(json_error('Not permitted to edit Layer.'))

@csrf_exempt
@login_required
def removeLayerViewer(request, layer_uid, token_uid):
    user_token_key = get_token_key(request)
    data = DataOperator(user_token_key)

    if data.has_layer_permissions(layer_uid, Role.OWNER):
        DataLayerRole.objects.filter(layer_id=layer_uid, role=Role.VIEWER, token_id=token_uid).delete()
        return HttpResponse(json_error('Removed access for token.'))
    else:
        return HttpResponse(json_error('Not permitted to edit Layer.'))

@csrf_exempt
@login_required
def addLayerToGeoview(request, geo_uid, layer_uid):
    user_token_key = get_token_key(request)
    data = DataOperator(user_token_key)

    if data.has_geoview_permissions(geo_uid, Role.EDITOR):
        message = data.add_layer_to_geoview(geo_uid, layer_uid)
        return HttpResponse(json_error(message))
    else:
        return HttpResponse(json_error('Not permitted to edit GeoView.'))

@csrf_exempt
@login_required
def removeLayerFromGeoview(request, geo_uid, layer_uid):
    user_token_key = get_token_key(request)
    data = DataOperator(user_token_key)

    if data.has_geoview_permissions(geo_uid, Role.EDITOR):
        message = data.remove_layer_from_geoview(geo_uid, layer_uid)
        return HttpResponse(json_error(message))
    else:
        return HttpResponse(json_error('Not permitted to edit GeoView.'))

@csrf_exempt
@login_required
def features(request):
    user_token_key = get_token_key(request)
    data = DataOperator(user_token_key)

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
@login_required
def fetchFromURL(request):
    user_token_key = get_token_key(request)
    data = DataOperator(user_token_key)
    importer = Importer(user_token_key)

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
@login_required
def getFeature(request, feature_uid):
    user_token_key = get_token_key(request)
    data = DataOperator(user_token_key)

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
@login_required
def getLayer(request, layer_uid):
    user_token_key = get_token_key(request)
    data = DataOperator(user_token_key)

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
@login_required
def getTokens(request):
    json_resp = to_json(DataOperator().get_apitokens())
    return HttpResponse(json_resp)

@csrf_exempt
@login_required
def getGeoview(request, geo_uid):

    user_token_key = get_token_key(request)
    data = DataOperator(user_token_key)

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
            geoview.token_key = user_token_key
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
@login_required
def uploadPage(request):
    form = UploadFileForm()
    context = {'form':form, 'STATIC_URL':STATIC_URL}
    return render(request, 'rapid/upload/uploadform.html', context)

@csrf_exempt
@login_required
def uploadFile(request):

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            handle_uploaded_file(request.FILES['file'], request.POST, request.session)
            context = {'form' : form,
                       'filename': request.FILES['file'].name,
                       'STATIC_URL':STATIC_URL,
                       'BASE_URL':BASE_URL}
            return render(request, 'rapid/upload/uploadsuccess.html', context)
        else:
            context = {'form' : form}
            return render(request, 'rapid/upload/formerrors.html', context)
    else:
        form = UploadFileForm()
        return HttpResponse(json_error('request.method != "POST"'))

def handle_uploaded_file(f, request, session):
    from rapid.settings import DROPBOX_DIR

    ext = f.name[-3:]

    file_path = os.path.join(DROPBOX_DIR, f.name)

    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    user_token_key = ApiToken.objects.get(uid=session.get('token')).key
    data = DataOperator(user_token_key)

    if request['des']:
        descriptor = request['des']
    else:
        descriptor = 'No descriptor provided'

    try:
        is_public = request['public']
    except:
        is_public = False

    try:
        properties = request['props']
    except:
        properties = None

    layer_uid = data.create_layer(descriptor, is_public, properties)

    role = DataLayerRole(layer_id=layer_uid, token=data.get_apitoken(), role=Role.OWNER)
    role.save()

    importer = Importer(user_token_key)

    if (ext.upper() == 'ZIP'):
        try:
            importer.import_shapefile(file_path, layer_uid)
        except:
            data.delete_layer(layer_uid)
            print "Shapefile import failed."
            return

    if (ext.upper() == 'JSON'):
        try:
            importer.import_geojson_file(file_path, layer_uid)
        except:
            data.delete_layer(layer_uid)
            print "GeoJSON import failed."
            return

    # Add featuretype to Geoserver
    if create_featuretype(layer_uid) is None:
        print 'WARNING: featureType {} was not successfully sent to Geoserver'.format(layer_uid)
        return

    if is_public == True:
        addGeofenceRule('*', descriptor)
    else:
        username = ApiToken.objects.get(uid=session.get('token')).descriptor
        addGeofenceRule(username, descriptor)

    return

def create_featuretype(uid):
    import rapid.gs as GS

    gs = GS.Geoserver()

    ft = gs.createFeatureTypeFromUid(uid)

    if ft is not None:
        response = gs.sendFeatureType(ft)

        if response.status_code == 201:
            location = response.headers['Location']
            return location
        else:
            return None
    else:
        return None

def register(request):

    """
        Taken from http://www.tangowithdjango.com/book17/chapters/login.html
    """

    # Get the request's context.
    context = RequestContext(request)

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():

            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            password = user.password
            user.set_password(user.password)
            user.save()

            # Now sort out the UserProfile instance.
            try:
                token = ApiToken.objects.get(descriptor=user_form.Meta.model.username)
            except:
                token = ApiToken()
                token.setup(user.username)
                token.save()


            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.token = token

            # Now we save the UserProfile model instance.
            profile.save()

            # Add user to Geofence for Geoserver authentication
            # TODO: Where does email come from?
            addGeofenceUser(user.username, password, None)

            # Update our variable to tell the template registration was successful.
            registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print user_form.errors, profile_form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the template depending on the context.
    return render_to_response(
            'rapid/register/register.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered}, context)

def user_login(request):
    """
        Taken from http://www.tangowithdjango.com/book17/chapters/login.html
    """
    from django.contrib.auth import authenticate, login

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
                # We use request.POST.get('<variable>') as opposed to request.POST['<variable>'],
                # because the request.POST.get('<variable>') returns None, if the value does not exist,
                # while the request.POST['<variable>'] will raise key error exception
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                request.session.set_test_cookie()
                login(request, user)
                request.session.set_expiry(300)
                return HttpResponseRedirect('/rapid/portal/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your RAPID account has been deactivated. Please contact your RAPID administrator.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        return render(request, 'rapid/login/login.html', {'STATIC_URL':STATIC_URL})

@login_required
def user_logout(request):
    """
    Logs the user out and redirects to login page.
    """
    from datetime import datetime
    from django.contrib.auth import logout

    request.session['last_visit_logout'] = str(datetime.now())

    logout(request)

    return HttpResponseRedi