
var test_f = false;

$(document).ready(function() {
  add_img($('#v1')[0], "vis06_s.png", 0);
  add_img($('#v2')[0], "vis08_s.png", 1);
  add_img($('#v3')[0], "vis16_s.png", 2);

  var ctx, data, ctxres;
  ctx = $('#v3')[0].getContext('2d');
  data = ctx.getImageData(0, 0, ctx.canvas.width, ctx.canvas.height);
//   ctxres = $('#res')[0].getContext('2d');
//   ctxres.canvas.width = ctx.canvas.width;
//   ctxres.canvas.height = ctx.canvas.height;
//   var numBytes = data.data.length;
//   console.log(numBytes);
//   var myImageData = ctxres.createImageData(ctx.canvas.width, ctx.canvas.height);
//   ctxres.putImageData(data, 0, 0);
});

function add_img(canvas, filename, rgb_index) {
  var img = new Image();
  img.onload = function(){
    canvas.width = img.width;
    canvas.height = img.height;
    canvas.getContext('2d').drawImage(img, 0, 0, img.width, img.height);
    var d = canvas.getContext('2d').getImageData(0, 0, img.width, img.height);

    if (test_f == false) {
      $('#res')[0].getContext('2d').createImageData(d);
      test_f = true; // MUST BE A BETTER WAY OF DOING THIS
    }
    var f = $('#res')[0].getContext('2d').getImageData(0, 0, img.width, img.height);
//    f.data = f.data + d.data * rgb_index;
    console.log(d.data);
    for (var i=0; i<d.data.length; i++) {
      f.data[i] = f.data[i] + d.data[i] * rgb_index;
    }
    console.log(f.data);
    $('#res')[0].getContext('2d').putImageData(f, 0, 0);
    var g = $('#res')[0].getContext('2d').getImageData(0, 0, img.width, img.height);
//    console.log(g);
  }
  img.src = filename;
}
