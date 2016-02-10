
var test_f = false;

$(document).ready(function() {
  add_img($('#v1')[0], "vis06_s.png", 2);
  add_img($('#v2')[0], "vis08_s.png", 1);
  add_img($('#v3')[0], "vis16_s.png", 0);
});

function add_img(canvas, filename, rgb_index) {
  var img = new Image();
  img.onload = function(){
    canvas.width = img.width;
    canvas.height = img.height;
    canvas.getContext('2d').drawImage(img, 0, 0, img.width, img.height);
    var d = canvas.getContext('2d').getImageData(0, 0, img.width, img.height);

    if (test_f == false) {
      $('#res')[0].getContext('2d').canvas.width = img.width;
      $('#res')[0].getContext('2d').canvas.height = img.height;
      $('#res')[0].getContext('2d').createImageData(d);
      test_f = true; // MUST BE A BETTER WAY OF DOING THIS
    }
    var f = $('#res')[0].getContext('2d').getImageData(0, 0, img.width, img.height);

    for (var i=0; i<d.data.length; i+=4) {
      f.data[i + rgb_index] = d.data[i];
      f.data[i + 3] = d.data[255];
    }
    $('#res')[0].getContext('2d').putImageData(f, 0, 0);
  }
  img.src = filename;
}
