from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from geonode.layers.models import Layer
from geonode.maps.models import MapLayer, Map as GeoNodeMap
from cartoview.app_manager.models import AppInstance
from django.utils.translation import ugettext_lazy as _

from django.template.defaultfilters import slugify
from . import APP_NAME

def publish_layer_group(geonode_map):
        """
        Publishes local map layers as WMS layer group on local OWS.
        """
        if 'geonode.geoserver' in settings.INSTALLED_APPS:
            from geonode.geoserver.helpers import gs_catalog
            from geoserver.layergroup import UnsavedLayerGroup as GsUnsavedLayerGroup
        else:
            raise Exception(
                'Cannot publish layer group if geonode.geoserver is not in INSTALLED_APPS')

        # temporary permission workaround:
        # only allow public maps to be published
        if not geonode_map.is_public:
            return 'Only public maps can be saved as layer group.'

        map_layers = MapLayer.objects.filter(map=geonode_map.id)

        # Local Group Layer layers and corresponding styles
        layers = []
        lg_styles = []
        for ml in map_layers:
            if ml.local:
                layer = Layer.objects.get(typename=ml.name)
                style = ml.styles or getattr(layer.default_style, 'name', '')
                layers.append(layer)
                lg_styles.append(style)
        lg_layers = [l.name for l in layers]

        # Group layer bounds and name

        lg_bounds = [
            str(min(geonode_map.bbox_x0,geonode_map.bbox_x1)), # xmin
            str(max(geonode_map.bbox_x0,geonode_map.bbox_x1)), # xmax
            str(min(geonode_map.bbox_y0,geonode_map.bbox_y1)), # ymin
            str(max(geonode_map.bbox_y0,geonode_map.bbox_y1)), # ymax
            str(geonode_map.srid)]
        # lg_bounds = [str(coord) for coord in geonode_map.bbox]

        lg_name = '%s_%d' % (slugify(geonode_map.title), geonode_map.id)

        # Update existing or add new group layer
        lg = geonode_map.layer_group
        if lg is None:
            lg = GsUnsavedLayerGroup(
                gs_catalog,
                lg_name,
                lg_layers,
                lg_styles,
                lg_bounds)
        else:
            lg.layers, lg.styles, lg.bounds = lg_layers, lg_styles, lg_bounds
        gs_catalog.save(lg)
        return lg_name

class MinMaxFloat(models.FloatField):
    def __init__(self, min_value=None, max_value=None, *args, **kwargs):
        self.min_value, self.max_value = min_value, max_value
        super(MinMaxFloat, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value, 'max_value' : self.max_value}
        defaults.update(kwargs)
        return super(MinMaxFloat, self).formfield(**defaults)

class HoverMap(AppInstance):
    template_help_text = _("You can define popup content using HTML, CSS and feature's fileds by specifying the field name in curly brackets, for example: {field_name}")
    # title = models.CharField(max_length=256, null=False, blank=False)
    map = models.ForeignKey(GeoNodeMap)
    layer = models.ForeignKey(Layer, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Hover Layer")
    # base_map = models.CharField(max_length=50, null=True, blank=True)
    hover_tpl = models.TextField(null=True, blank=True, verbose_name="Hover Template", help_text=template_help_text)
    opacity = MinMaxFloat(min_value=0.0, max_value=1.0, default=1.0)
    enable_popup = models.BooleanField(default=True, verbose_name="Show Pop-up")
    enable_hover = models.BooleanField(default=True, verbose_name="Show Hover Info")
    enable_legend = models.BooleanField(default=False, verbose_name="Show legend")
    default_legend = models.BooleanField(default=True)
    legend = models.ImageField(upload_to='%s/' % APP_NAME,null=True, blank=True, verbose_name="Custom legend")
