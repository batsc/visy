
$(document).ready(function() {
  add_img($('#v1')[0], "images/vis06.png");
  add_img($('#v2')[0], "images/vis08.png");
  add_img($('#v3')[0], "images/vis16.png");

  var ctx, data;
  ctx = $('#v3')[0].getContext('2d');
  data = ctx.getImageData(0, 0, ctx.canvas.width, ctx.canvas.height);
});

function add_img(canvas, filename) {
  var img = new Image();
  img.onload = function(){
    canvas.width = img.width;
    canvas.height = img.height;
    canvas.getContext('2d').drawImage(img, 0, 0, img.width, img.height);
  }
  img.src = filename;
}
