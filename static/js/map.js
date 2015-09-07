
var geotiffTypeOptions = {
  getTileUrl: function(coord, zoom) {return '/api/v0/zoom/'+zoom+'/tile/' + coord.x + '/' + coord.y + '/jpg/';},
  tileSize: new google.maps.Size(128,128),
  maxZoom: 15,
  minZoom: 0,
  radius: 6371000,
  name: 'geotiff'
};

var geotiffMapType = new google.maps.ImageMapType(geotiffTypeOptions);

function initialize() {
  var myLatlng = new google.maps.LatLng(48, 55);
  var mapOptions = {
    center: myLatlng,
    zoom: 0,
    streetViewControl: false,
    mapTypeControlOptions: {
      mapTypeIds: ['geotiff']
    }
  };

  var map = new google.maps.Map(document.getElementById('map-canvas'),
      mapOptions);
  map.mapTypes.set('geotiff', geotiffMapType);
  map.setMapTypeId('geotiff');
}

google.maps.event.addDomListener(window, 'load', initialize);
