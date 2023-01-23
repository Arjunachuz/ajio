let autocomplete;

function initAutoComplete(){
autocomplete = new google.maps.places.Autocomplete(
    document.getElementById('id_address'),
    {
        types: ['geocode', 'establishment'],
        componentRestrictions: {'country': ['in']},
    })
    //prediction clicked
autocomplete.addListener('place_changed', onPlaceChanged);
}

function onPlaceChanged (){
    var place = autocomplete.getPlace();

    if (!place.geometry){
        document.getElementById('id_address').palceholder = "Start Typing...";
    }
    else{
       
    }
    // console.log(place)

    var geocoder = new google.maps.Geocoder()
    var address = document.getElementById('id_address').value

    geocoder.geocode({'address':address}, function(results, status){
        // console.log('results:',results)
        
        if(status == google.maps.GeocoderStatus.OK){
            // console.log('status:',status)
            var latitude = results[0].geometry.location.lat();
            var longitude = results[0].geometry.location.lng();

            // console.log('lat:',latitude);
            // console.log('lng:',longitude);
            $('#id_latitude').val(latitude);
            $('#id_longitude').val(longitude);
        }
    })
} 