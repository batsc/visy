// Settings
var init_lineWidth = 2;
var hover_lineWidth = 5;

// Temporary scaling settings (EW area)
var topleftlat = 61.434;
var topleftlon = -44.790;
var botrighlat = 32.754;
var botrighlon = 17.194;

var mx,cx,my,cy;

// Constructor for Shape objects to hold data for all drawn objects.
function Shape(coords, stroke_color, name) {
  this.coords = coords;
  this.stroke_color = stroke_color || '#AA0000';
  this.name = name || 'null';
  this.active = false;
}

// Draws this shape to a given context
Shape.prototype.draw = function(ctx, selected) {
  var x,y;
  [x, y] = geo_to_stereo(this.coords[0][1], this.coords[0][0]);
  ctx.beginPath();
  ctx.moveTo(mx * x + cx, ctx.canvas.height - (my * y + cy));
  for (var i=1; i<this.coords.length; i++) {
    [x, y] = geo_to_stereo(this.coords[i][1], this.coords[i][0]);
    ctx.lineTo(mx * x + cx, ctx.canvas.height - (my * y + cy));
  }
  ctx.closePath();
  ctx.strokeStyle = this.stroke_color;

  // If this shape is hovered over
  if (selected) {
    ctx.lineWidth = hover_lineWidth;
  }
  else {
    ctx.lineWidth = init_lineWidth;
  }
  ctx.stroke();
}


function CanvasState(canvas) {
  // Setup
  var [leftlim, uplim] = geo_to_stereo(topleftlon, topleftlat);
  var [rightlim, botlim] = geo_to_stereo(botrighlon, botrighlat);
  this.canvas = canvas;
  this.width = canvas.width;
  this.height = canvas.height;
  this.ctx = canvas.getContext('2d');
  mx = this.width / (rightlim - leftlim);
  cx = this.width - mx * rightlim;
  my = this.height / (uplim - botlim);
  cy = this.height - my * uplim;

  // This complicates things a little but but fixes mouse co-ordinate problems
  // when there's a border or padding. See getMouse for more detail
  var stylePaddingLeft, stylePaddingTop, styleBorderLeft, styleBorderTop;
  if (document.defaultView && document.defaultView.getComputedStyle) {
    this.stylePaddingLeft = parseInt(
      document.defaultView.getComputedStyle(canvas, null)['paddingLeft'], 10)      || 0;
    this.stylePaddingTop  = parseInt(
      document.defaultView.getComputedStyle(canvas, null)['paddingTop'], 10)       || 0;
    this.styleBorderLeft  = parseInt(
      document.defaultView.getComputedStyle(canvas, null)['borderLeftWidth'], 10)  || 0;
    this.styleBorderTop   = parseInt(
      document.defaultView.getComputedStyle(canvas, null)['borderTopWidth'], 10)   || 0;
  }
  // Some pages have fixed-position bars (like the stumbleupon bar) at the top or left
  // of the page. They will mess up mouse coordinates and this fixes that.
  var html = document.body.parentNode;
  this.htmlTop = html.offsetTop;
  this.htmlLeft = html.offsetLeft;

  this.shapes = [];  // the collection of shapes

  // **** Then events! ****

  // This is an example of a closure!
  // Right here "this" means the CanvasState. But we are making events on the Canvas itself,
  // and when the events are fired on the canvas the variable "this" is going to mean the
  // canvas! Since we still want to use this particular CanvasState in the events we have
  // to save a reference to it. This is our reference!
  var myState = this;

  // Fixes a problem where double clicking causes text to get selected on the canvas
  canvas.addEventListener('selectstart', function(e) {
    e.preventDefault(); return false;
  }, false);

  // Redraw the canvas if mouse move - necessary to detect if mouse is over
  // a shape
  canvas.addEventListener('mousemove', function(e) {
    var mouse = myState.getMouse(e);
    myState.draw(mouse);
  }, true);

  // If within a shape, show that shape's data in the info box
  canvas.addEventListener('mousedown', function(e) {
    for (var i = 0; i < myState.shapes.length; i++) {
      if (myState.shapes[i].active) {
        $('#info_area').html(myState.shapes[i].name);
      }
    }
  }, true);
}

CanvasState.prototype.addShape = function(shape) {
  this.shapes.push(shape);
}

CanvasState.prototype.clear = function() {
  this.ctx.clearRect(0, 0, this.width, this.height);
}

CanvasState.prototype.draw = function(mouse) {

  var ctx = this.ctx;
  var shapes = this.shapes;
  this.clear();

  // Draw all shapes
  for (var i = 0; i < shapes.length; i++) {
    var shape = shapes[i];
    shapes[i].draw(ctx);

    if (mouse) {
      if (ctx.isPointInPath(mouse.x, mouse.y)) {
        shapes[i].active = true;
        shapes[i].draw(ctx, 'selected');
      }
      else {
        shapes[i].active = false;
      }
    }
  }

  // If mouse hovering over any active region, set cursor
  if (shapes.some(function(element) {return element.active==true;})) {
    ctx.canvas.style.cursor = 'pointer';
  }
  else {
    ctx.canvas.style.cursor = 'default';
  }
}


// Creates an object with x and y defined, set to the mouse position relative to the
// state's canvas. If you wanna be super-correct this can be tricky, we have to worry
// about padding and borders.
CanvasState.prototype.getMouse = function(e) {
  var element = this.canvas, offsetX = 0, offsetY = 0, mx, my;

  // Compute the total offset
  if (element.offsetParent !== undefined) {
    do {
      offsetX += element.offsetLeft;
      offsetY += element.offsetTop;
    } while ((element = element.offsetParent));
  }

  // Add padding and border style widths to offset
  // Also add the <html> offsets in case there's a position:fixed bar
  offsetX += this.stylePaddingLeft + this.styleBorderLeft + this.htmlLeft;
  offsetY += this.stylePaddingTop + this.styleBorderTop + this.htmlTop;

  mx = e.pageX - offsetX;
  my = e.pageY - offsetY;

  // We return a simple javascript object (a hash) with x and y defined
  return {x: mx, y: my};
}

// Converts from degrees to radians.
Math.radians = function(degrees) {
  return degrees * Math.PI / 180;
};
 
// Converts from radians to degrees.
Math.degrees = function(radians) {
  return radians * 180 / Math.PI;
};

// Convert geographic coords to stereographic view
function geo_to_stereo(lon, lat){
  var lon0 = 0;
  var lat0 = 90;
  var x = Math.sin(Math.radians(lon - lon0)) *
          Math.tan(Math.radians(90 - lat)) / 2;
  var y = Math.cos(Math.radians(lon - lon0)) *
          Math.tan(Math.radians(90 - lat)) / 2;
  return [x,y];
}

// When document ready...
$(document).ready(function() {
      
  var s = new CanvasState(document.getElementById('canvas'));

  $.getJSON('features.json')
    .done(function(data) {
      $.each(data, function(feature_name, feature_data) {
        s.addShape(new Shape(feature_data.coords, feature_data.strokeStyle,
                             feature_name));
        s.draw();
      })
    })
    .fail(function() {
      console.log('Could not load features data');
    });
});

