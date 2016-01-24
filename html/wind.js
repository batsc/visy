

$( document ).ready(function() {
  var ctx = $('#canvas')[0].getContext('2d');
  var img_src = "/home/batsc/Work/git/WorldWeatherSymbols/symbols/ddff_WindArrows/WeatherSymbol_WMO_WindArrowNH_47.svg";

  var img = new Image();
  img.onload = function() {
    drawRotatedImage(ctx, img, 10, 10, 45);
  }
  img.src = img_src;
});

var TO_RADIANS = Math.PI/180;
function drawRotatedImage(ctx, img, x, y, angle)
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
    ctx.drawImage(img,  -(img.width/2), -(img.height/2));

    // and restore the co-ords to how they were when we began
    ctx.restore();
}