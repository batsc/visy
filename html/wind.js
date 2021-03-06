
var img = new Image();

$( document ).ready(function() {
  var ctx = $('#canvas')[0].getContext('2d');
  var img_src = "/home/batsc/Work/git/WorldWeatherSymbols/symbols/ddff_WindArrows/WeatherSymbol_WMO_WindArrowNH_47.svg";

  var wd = 110;
  var ht = 36;
  img.onload = function() {
    for (var j=0;j<20;j++) {
      for (var i=0;i<9;i++) {
        drawRotatedImage(ctx, img, (wd + j*wd)/2, ht + i*ht, (i + j*9) * 2, wd, ht);
      }
    }
  }
  img.src = img_src;
});

var TO_RADIANS = Math.PI/180;
function drawRotatedImage(ctx, img, x, y, angle, dheight, dwidth)
{
    // save the current co-ordinate system
    // before we screw with it
    ctx.save();

    // move to the middle of where we want to draw our image
    ctx.translate(x, y);

    // rotate around that point, converting our
    // angle from degrees to radians
    ctx.rotate(angle * TO_RADIANS);

    // draw it up and to the left by half the width
    // and height of the image
    ctx.drawImage(img,  -(dwidth/2), -(dheight/2), dwidth, dheight);

    // and restore the co-ords to how they were when we began
    ctx.restore();
}