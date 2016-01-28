/**
 * Created by Mohamed on 1/27/2016.
 */

    var map = L.map('map').setView([MAP_Y, MAP_X], MAP_ZOOM);

    var googleMapGrayscale = new L.Google('ROADMAP', {
        mapOptions: {
            styles: [{"featureType":"water","elementType":"geometry","stylers":[{"color":"#e9e9e9"},{"lightness":17}]},{"featureType":"landscape","elementType":"geometry","stylers":[{"color":"#f5f5f5"},{"lightness":20}]},{"featureType":"road.highway","elementType":"geometry.fill","stylers":[{"color":"#ffffff"},{"lightness":17}]},{"featureType":"road.highway","elementType":"geometry.stroke","stylers":[{"color":"#ffffff"},{"lightness":29},{"weight":0.2}]},{"featureType":"road.arterial","elementType":"geometry","stylers":[{"color":"#ffffff"},{"lightness":18}]},{"featureType":"road.local","elementType":"geometry","stylers":[{"color":"#ffffff"},{"lightness":16}]},{"featureType":"poi","elementType":"geometry","stylers":[{"color":"#f5f5f5"},{"lightness":21}]},{"featureType":"poi.park","elementType":"geometry","stylers":[{"color":"#dedede"},{"lightness":21}]},{"elementType":"labels.text.stroke","stylers":[{"visibility":"on"},{"color":"#ffffff"},{"lightness":16}]},{"elementType":"labels.text.fill","stylers":[{"saturation":36},{"color":"#333333"},{"lightness":40}]},{"elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"transit","elementType":"geometry","stylers":[{"color":"#f2f2f2"},{"lightness":19}]},{"featureType":"administrative","elementType":"geometry.fill","stylers":[{"color":"#fefefe"},{"lightness":20}]},{"featureType":"administrative","elementType":"geometry.stroke","stylers":[{"color":"#fefefe"},{"lightness":17},{"weight":1.2}]}]
        }
    });
    map.addLayer(googleMapGrayscale);

    var wmslayer = L.tileLayer.wms(GEOSERVER_BASE_URL + "wms", {
        layers: MAP_NAME,
        format: 'image/png',
        transparent: true,
        SrsName : 'EPSG:4326',
        version: '1.1.0'
    });
    wmslayer.setOpacity(OPACITY)
    wmslayer.addTo(map);

    // control that shows state info on hover
    var info = L.control();

    info.onAdd = function (map) {
        this._div = L.DomUtil.create('div', 'info');
        this.update();
        return this._div;
    };

    info.update = function (props) {
        if (props) {
            $(this._div).show();
            this._div.innerHTML = template(hover_template, props);
        }
        else
            $(this._div).hide();
    };

    info.addTo(map);

    function style(feature) {
        return {
            opacity: 0,
            fillOpacity: 0
        };
    }
    var layerPopup;
    var popup_content = "";
    function highlightFeature(e) {
        var layer = e.target;
        if(layer.feature.geometry.type == 'Polygon' || layer.feature.geometry.type == 'MultiPolygon') {
            layer.setStyle({
                weight: 2,
                opacity: 1,
                color: '#999',
                dashArray: '',
                fillOpacity: 0
            });
            if (!L.Browser.ie && !L.Browser.opera) {
                layer.bringToFront();
            }
        }
        if(HOVER_ENABLED == "True")
            info.update(layer.feature.properties);
    }

    var geojson;

    function resetHighlight(e) {
        geojson.resetStyle(e.target);
        info.update();
    }

    function clickFeature(e) {
        var layer = e.target;
        if(POPUP_ENABLED == "True"){
            popup_content = template(hover_template,layer.feature.properties);
            layer.bindPopup(popup_content,{className: 'custom-popup'}).openPopup();
        }
    }

    function onEachFeature(feature, layer) {
        layer.on({
            mouseover: highlightFeature,
            mouseout: resetHighlight,
            click: clickFeature
        });
    }

    function loadGeoJson(data) {
        geojson = L.geoJson(data, {
            style: style,
            pointToLayer: function(feature, latlng) {
                return new L.CircleMarker(latlng, {radius: 10, fillOpacity: 0});
            },
            onEachFeature: onEachFeature
        }).addTo(map);
        /* Zoom to layer */
        // map.fitBounds(geojson.getBounds());
    }

    var featureParameters = {
        service : 'WFS',
        version : '1.1.0',
        request : 'GetFeature',
        typeName : HOVER_LAYER_NAME,
        SrsName : 'EPSG:4326',
        outputFormat : 'json'
    };

    if(HOVER_LAYER_NAME != '') {
        var url = PROXY_URL + GEOSERVER_BASE_URL + "ows?" + encodeURIComponent($.param(featureParameters));
        $.ajax({
            type: 'GET',
            url: url,
            success: function(data) {
                loadGeoJson(data);
                $('body').removeClass('app-loading');
            }
        });

        if(LEGEND_ENABLED == "True") {
            var legend = L.control({position: 'bottomright'});
            legend.onAdd = function (map) {
                var div = L.DomUtil.create('div', 'info legend');
                if (DEFAULT_LEGEND == "True") {
                    if (STYLES != '')
                        div.innerHTML = '<img src="' + GEOSERVER_BASE_URL + 'wms?request=GetLegendGraphic&format=image/png&LAYER=' + HOVER_LAYER_NAME + '&style=' + STYLES + '">';
                    else
                        div.innerHTML = '<img src="' + GEOSERVER_BASE_URL + 'wms?request=GetLegendGraphic&format=image/png&LAYER=' + HOVER_LAYER_NAME + '">';
                }
                else if (LAYER_LEGEND != '') {
                    div.innerHTML = '<img src="' + MEDIA_URL + LAYER_LEGEND + '" alt="' + MEDIA_URL + LAYER_LEGEND + '"/>';
                }
                return div;
            };
            legend.addTo(map);
        }
    }
    else
        alert("Hover layer does not Exist");

    function template (str, data) {
        return str.replace(/\{ *([\w_]+) *\}/g, function (str, key) {
            try {
                var value = data[key];
                if (value === undefined) {
                    throw new Error('No value provided for variable ' + str);
                } else if (typeof value === 'function') {
                    value = value(data);
                }
                return value;
            }
            catch(err) {
                return 'No value provided for variable ' + str
            }
        });
    }