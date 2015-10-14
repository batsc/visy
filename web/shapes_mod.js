// By Simon Sarris
// www.simonsarris.com
// sarris@acm.org
//
// Last update December 2011
//
// Free to use and distribute at will
// So long as you are nice to people, etc

// Settings
var init_lineWidth = 2;
var hover_lineWidth = 5;

// Constructor for Shape objects to hold data for all drawn objects.
function Shape(coords, stroke_color, name) {
  this.coords = coords;
  this.stroke_color = stroke_color || '#AAAAAA';
  this.name = name || 'null';
}

// Draws this shape to a given context
Shape.prototype.draw = function(ctx) {
  ctx.beginPath();
  ctx.moveTo(this.coords[0][0],this.coords[0][1]);
  for (var i=1; i<this.coords.length; i++) {
    ctx.lineTo(this.coords[i][0],this.coords[i][1]);
  }
  ctx.closePath();
  ctx.strokeStyle = this.stroke_color;
  ctx.lineWidth = init_lineWidth;
  ctx.stroke();
}


function CanvasState(canvas) {
  // **** First some setup! ****
  
  this.canvas = canvas;
  this.width = canvas.width;
  this.height = canvas.height;
  this.ctx = canvas.getContext('2d');
  // This complicates things a little but but fixes mouse co-ordinate problems
  // when there's a border or padding. See getMouse for more detail
  var stylePaddingLeft, stylePaddingTop, styleBorderLeft, styleBorderTop;
  if (document.defaultView && document.defaultView.getComputedStyle) {
    this.stylePaddingLeft = parseInt(document.defaultView.getComputedStyle(canvas, null)['paddingLeft'], 10)      || 0;
    this.stylePaddingTop  = parseInt(document.defaultView.getComputedStyle(canvas, null)['paddingTop'], 10)       || 0;
    this.styleBorderLeft  = parseInt(document.defaultView.getComputedStyle(canvas, null)['borderLeftWidth'], 10)  || 0;
    this.styleBorderTop   = parseInt(document.defaultView.getComputedStyle(canvas, null)['borderTopWidth'], 10)   || 0;
  }
  // Some pages have fixed-position bars (like the stumbleupon bar) at the top or left of the page
  // They will mess up mouse coordinates and this fixes that
  var html = document.body.parentNode;
  this.htmlTop = html.offsetTop;
  this.htmlLeft = html.offsetLeft;

  this.shapes = [];  // the collection of shapes
  
  // **** Then events! ****
  
  // This is an example of a closure!
  // Right here "this" means the CanvasState. But we are making events on the Canvas itself,
  // and when the events are fired on the canvas the variable "this" is going to mean the canvas!
  // Since we still want to use this particular CanvasState in the events we have to save a reference to it.
  // This is our reference!
  var myState = this;
  
  //fixes a problem where double clicking causes text to get selected on the canvas
  canvas.addEventListener('selectstart', function(e) { e.preventDefault(); return false; }, false);

  canvas.addEventListener('mousemove', function(e) {
    myState.draw();
    var mouse = myState.getMouse(e);

    if ( myState.ctx.isPointInPath(mouse.x, mouse.y) ) {
      $('#info_area').html('yikes');
    }
    else {
      $('#info_area').html('oops');
    }
  }, true);
}

CanvasState.prototype.addShape = function(shape) {
  this.shapes.push(shape);
}

CanvasState.prototype.clear = function() {
  this.ctx.clearRect(0, 0, this.width, this.height);
}

CanvasState.prototype.draw = function() {

    var ctx = this.ctx;
    var shapes = this.shapes;
    this.clear();

    // draw all shapes
    var l = shapes.length;
    for (var i = 0; i < l; i++) {
      var shape = shapes[i];
      shapes[i].draw(ctx);
    }

    // draw selection
    // right now this is just a stroke along the edge of the selected Shape
// \\    if (this.selection != null) {
// \\      ctx.strokeStyle = this.selectionColor;
// \\      ctx.lineWidth = this.selectionWidth;
// \\      var mySel = this.selection;
//      ctx.strokeRect(mySel.x,mySel.y,mySel.w,mySel.h);
// \\    }
}


// Creates an object with x and y defined, set to the mouse position relative to the state's canvas
// If you wanna be super-correct this can be tricky, we have to worry about padding and borders
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


// When document ready...
$( document ).ready(function() {

  var s = new CanvasState(document.getElementById('canvas'));

  $.getJSON('features.json')
    .done( function( data ) {
      $.each( data, function( feature_name, feature_data ) {
        s.addShape(new Shape(feature_data.coords, feature_data.strokeStyle, feature_name));
        s.draw();
      })
    })
    .fail( function() {
      console.log('Could not load features data');
    });
});
