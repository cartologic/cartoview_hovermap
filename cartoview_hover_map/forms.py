from .models import HoverMap
from django import forms
from geonode.layers.models import Layer
from cartoview.app_manager.forms import AppInstanceForm

class NewMapForm(AppInstanceForm):
    layer = forms.CharField(widget=forms.Select(choices=[], attrs={'class':'map_layers'}))

    class Meta(AppInstanceForm.Meta):
        model = HoverMap
        fields = AppInstanceForm.Meta.fields + ['map', 'layer', 'hover_tpl', 'opacity', 'enable_popup', 'enable_hover', 'enable_legend', 'default_legend', 'legend']

    def clean_layer(self):
        layer = self.cleaned_data['layer']
        layer = Layer.objects.get(typename=layer)
        return layer