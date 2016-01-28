/**
 * Created by Mohamed on 1/21/2016.
 */

    $(document).ready(function(){
        if($("[name='map']").val() != ""){
            getLayers($("[name='map']").val());
        }
        else{
            $("[name='layer']").html('');
        }
    });

    $('input[name="enable_legend"]').on('change', function() {
        $("#ct-legend").toggle(this.checked);
    });

    $("[name='map']").on('change', function() {
        if(this.value) {
            getLayers(this.value);
        }
        else {
            $("[name='layer']").html('');
        }
    });

    function getLayers(map_id) {
        url = URL.replace('0', map_id);
        $.getJSON(url, function(data) {
            var opt=$("[name='layer']");
            opt.html('');
            opt.append($('<option/>'));
            $.each(data, function () {
                layer_params = obj = jQuery.parseJSON(this.fields.layer_params)
                opt.append($('<option/>').val(this.fields.name).text(layer_params.title).attr('data-style',this.fields.styles));
            });
            if(SELECTED_LAYER)
                $("[name='layer']").val(SELECTED_LAYER);
        });
    }
