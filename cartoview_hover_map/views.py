from django.shortcuts import render_to_response, HttpResponse, redirect, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from geonode.layers.models import Layer
from django.conf import settings
from .forms import NewMapForm
from .models import HoverMap, publish_layer_group
from django.contrib.gis.geos import Point
from cartoview.app_manager.models import *
from . import APP_NAME

from geonode.maps.models import MapLayer
import json

VIEW_TPL = "%s/view.html" % APP_NAME
EMBED_TPL = "%s/embed.html" % APP_NAME
NEW_EDIT_TPL = "%s/new.html" % APP_NAME
LIST_TPL = "%s/list.html" % APP_NAME

def map_context(map_id):
    map_layer = HoverMap.objects.get(appinstance_ptr_id=map_id)
    _map = map_layer.map
    _layer = map_layer.layer
    style = ""
    if (_layer):
        style = MapLayer.objects.get(map=_map, name=_layer.typename).styles

    try:
        layer_group_name = publish_layer_group(map_layer.map)
    except:
        layer_group_name = ""
    # convert map center projection from 900913 to 4326
    map_center = Point(map_layer.map.center_x, map_layer.map.center_y, srid=900913)
    map_center.transform(4326)
    context = {
        'map_name': layer_group_name,
        'map_center':map_center,
        'map_layer': map_layer,
        'hover_layer': map_layer.layer,
        'styles': style
    }
    return context

def view_map(request, map_id):
    return render_to_response(VIEW_TPL, map_context(map_id), context_instance=RequestContext(request))

def embed_map(request, map_id):
    return render_to_response(EMBED_TPL, map_context(map_id), context_instance=RequestContext(request))

def new_map(request):
    if request.method == 'POST':
        _form = NewMapForm(request.POST, request.FILES)
        if _form.is_valid():
            new_form = _form.save(commit=False)
            new_form.app = App.objects.get(name=APP_NAME)
            new_form.owner = request.user
            new_form.save()
            return HttpResponseRedirect(reverse('appinstance_detail', kwargs={'appinstanceid': new_form.pk}))
        else:
            context = {'map_form': _form, 'error':_form.errors}
    else:
        map_form = NewMapForm()
        context = {'map_form': map_form, 'oper':'new'}
    return render_to_response(NEW_EDIT_TPL, context, context_instance=RequestContext(request))


def edit_map(request, map_id):
    map_layer = HoverMap.objects.get(appinstance_ptr_id=map_id)
    if request.method == 'POST':
        _form = NewMapForm(request.POST, request.FILES, instance=map_layer)
        if _form.is_valid():
            new_form = _form.save()
            return HttpResponseRedirect(reverse('appinstance_detail', kwargs={'appinstanceid':new_form.pk}))
        else:
            context = {'map_form': _form, 'error':_form.errors}
    else:
        map_form = NewMapForm(instance=map_layer)
        context = {'map_form': map_form, 'name':map_layer.title, 'oper':'edit', 'layer_name':map_layer.layer.typename}
    return render_to_response(NEW_EDIT_TPL, context, context_instance=RequestContext(request))

def map_list(request):
    maps = HoverMap.objects.all()
    context = {'maps': maps}
    return render_to_response(LIST_TPL, context, context_instance=RequestContext(request))

from django.core import serializers

def map_layers(request, map_id):
    layers = MapLayer.objects.filter(map_id=map_id, fixed=False)
    data = serializers.serialize("json", layers)
    return HttpResponse(data, content_type='application/json')