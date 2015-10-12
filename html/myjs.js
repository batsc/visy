

look at 

http://simonsarris.com/blog/510-making-html5-canvas-useful



var canv_id = "drawing_canvas";
var in_area = false;

// Wait for document ready
$( document ).ready(function() {

  // Get canvas context
  var canvas = document.getElementById(canv_id);
  var ctx = canvas.getContext("2d");

  // Draw
  poly = new Path2D();
  poly.rect(50, 25, 150, 100);
  ctx.stroke();

  canvas.addEventListener("mousemove", function(event){
//     var rect = poly.getBoundingClientRect();
    var x = event.clientX - $("#" + canv_id).offset().left;
    var y = event.clientY - $("#" + canv_id).offset().top;

    if ( ctx.isPointInPath(poly, x, y) && in_area == false) {
      console.log('X:' + parseInt(x) + 'Y:' + parseInt(y));
      in_area = true;
    }
    else {
      in_area = false;
    }
  });

// ctx.beginPath();
// ctx.arc(100, 100, 75, 0, 2 * Math.PI, false);
// ctx.lineWidth = 5;
// ctx.stroke();
// 
// // eyes
// ctx.beginPath();
// ctx.arc(70, 80, 10, 0, 2 * Math.PI, false);
// ctx.arc(130, 80, 10, 0, 2 * Math.PI, false);
// ctx.fill();
// ctx.addHitRegion({id: "eyes"});
// 
// // mouth
// ctx.beginPath();
// ctx.arc(100, 110, 50, 0, Math.PI, false);
// ctx.stroke();

//   Firefox 30+ This feature is behind a feature preference setting.
//   In about:config, set canvas.hitregions.enabled to true.

/*  poly = new Path2D();
  poly.rect(50, 25, 150, 100);
  ctx.addHitRegion(poly, id='poly1', cursor='pointer');*/
});