MochiKit.DragAndDrop.Resizables = {
    /***

    Manage draggables elements. Not intended to direct use.

    ***/
    drags: [],

    register: function (draggable) {
        if (this.drags.length === 0) {
            var conn = MochiKit.Signal.connect;
            this.eventMouseUp = conn(document, 'onmouseup', this, this.endDrag);
            this.eventMouseMove = conn(document, 'onmousemove', this,
                                       this.updateDrag);
            this.eventKeypress = conn(document, 'onkeypress', this,
                                      this.keyPress);
        }
        this.drags.push(draggable);
    },

    unregister: function (draggable) {
        this.drags = MochiKit.Base.filter(function (d) {
            return d != draggable;
        }, this.drags);
        if (this.drags.length === 0) {
            var disc = MochiKit.Signal.disconnect;
            disc(this.eventMouseUp);
            disc(this.eventMouseMove);
            disc(this.eventKeypress);
        }
    },

    activate: function (draggable) {
        // allows keypress events if window is not currently focused
        // fails for Safari
        window.focus();
        this.activeResizable = draggable;
    },

    deactivate: function () {
        this.activeResizable = null;
    },

    updateDrag: function (event) {
        if (!this.activeResizable) {
            return;
        }
        var pointer = event.mouse();
        // Mozilla-based browsers fire successive mousemove events with
        // the same coordinates, prevent needless redrawing (moz bug?)
        if (this._lastPointer && (MochiKit.Base.repr(this._lastPointer.page) ==
                                  MochiKit.Base.repr(pointer.page))) {
            return;
        }
        this._lastPointer = pointer;
        this.activeResizable.updateDrag(event, pointer);
    },

    endDrag: function (event) {
        if (!this.activeResizable) {
            return;
        }
        this._lastPointer = null;
        this.activeResizable.endDrag(event);
        this.activeResizable = null;
    },

    keyPress: function (event) {
        if (this.activeResizable) {
            this.activeResizable.keyPress(event);
        }
    },

    notify: function (eventName, draggable, event) {
        MochiKit.Signal.signal(this, eventName, draggable, event);
    }
};

/** @id MochiKit.DragAndDrop.Resizable */
MochiKit.DragAndDrop.Resizable = function (element, options) {
    var cls = arguments.callee;
    if (!(this instanceof cls)) {
        return new cls(element, options);
    }
    this.__init__(element, options);
};

MochiKit.DragAndDrop.Resizable.prototype = {
    /***

    A draggable object. Simple instantiate :

        new MochiKit.DragAndDrop.Resizable('myelement');

    ***/
    __class__ : MochiKit.DragAndDrop.Resizable,

    __init__: function (element, /* optional */options) {
        var v = MochiKit.Visual;
        var b = MochiKit.Base;
        options = b.update({

            /** @id MochiKit.DragAndDrop.handle */
            handle: false,

            /** @id MochiKit.DragAndDrop.starteffect */
            starteffect: function (innerelement) {
                this._savedOpacity = MochiKit.Style.getStyle(innerelement, 'opacity') || 1.0;
                new v.Opacity(innerelement, {duration:0.2, from:this._savedOpacity, to:0.7});
            },
            /** @id MochiKit.DragAndDrop.reverteffect */
            reverteffect: function (innerelement, top_offset, left_offset) {
                var dur = Math.sqrt(Math.abs(top_offset^2) +
                          Math.abs(left_offset^2))*0.02;
                return new v.Move(innerelement,
                            {x: -left_offset, y: -top_offset, duration: dur});
            },

            /** @id MochiKit.DragAndDrop.endeffect */
            endeffect: function (innerelement) {
                new v.Opacity(innerelement, {duration:0.2, from:0.7, to:this._savedOpacity});
            },

            /** @id MochiKit.DragAndDrop.onchange */
            onchange: b.noop,

            /** @id MochiKit.DragAndDrop.zindex */
            zindex: 1000,

            /** @id MochiKit.DragAndDrop.revert */
            revert: false,

            /** @id MochiKit.DragAndDrop.scroll */
            scroll: false,

            /** @id MochiKit.DragAndDrop.scrollSensitivity */
            scrollSensitivity: 20,

            /** @id MochiKit.DragAndDrop.scrollSpeed */
            scrollSpeed: 15,
            // false, or xy or [x, y] or function (x, y){return [x, y];}

            /** @id MochiKit.DragAndDrop.snap */
            snap: false,
            
            /** @id MochiKit.DragAndDrop.Resizable.min **/
            min: [0, 0],

            /** @id MochiKit.DragAndDrop.Resizable.max **/
            max: false
        }, options);

        var d = MochiKit.DOM;
        this.element = d.getElement(element);

        if (options.handle && (typeof(options.handle) == 'string')) {
            this.handle = d.getFirstElementByTagAndClassName(null,
                                       options.handle, this.element);
        }
        if (!this.handle) {
            this.handle = d.getElement(options.handle);
        }
        if (!this.handle) {
            this.handle = this.element;
        }

        if (options.scroll && !options.scroll.scrollTo && !options.scroll.outerHTML) {
            options.scroll = d.getElement(options.scroll);
            this._isScrollChild = MochiKit.DOM.isChildNode(this.element, options.scroll);
        }

        d.makePositioned(this.element);  // fix IE

        this.delta = this.currentDelta();
        this.options = options;
        this.dragging = false;

        this.eventMouseDown = MochiKit.Signal.connect(this.handle,
                              'onmousedown', this, this.initDrag);
        MochiKit.DragAndDrop.Resizables.register(this);
    },

    /** @id MochiKit.DragAndDrop.destroy */
    destroy: function () {
        MochiKit.Signal.disconnect(this.eventMouseDown);
        MochiKit.DragAndDrop.Resizables.unregister(this);
    },

    /** @id MochiKit.DragAndDrop.currentDelta */
    currentDelta: function () {
        var s = MochiKit.Style.getStyle;
        return [
          parseInt(s(this.element, 'left') || '0'),
          parseInt(s(this.element, 'top') || '0')];
    },

    /** @id MochiKit.DragAndDrop.initDrag */
    initDrag: function (event) {
        if (!event.mouse().button.left) {
            return;
        }
        // abort on form elements, fixes a Firefox issue
        var src = event.target();
        var tagName = (src.tagName || '').toUpperCase();
        if (tagName === 'INPUT' || tagName === 'SELECT' ||
            tagName === 'OPTION' || tagName === 'BUTTON' ||
            tagName === 'TEXTAREA') {
            return;
        }

        if (this._revert) {
            this._revert.cancel();
            this._revert = null;
        }

        var pointer = event.mouse();
        var pos = MochiKit.Position.cumulativeOffset(this.element);
        this.offset = [pointer.page.x - pos.x, pointer.page.y - pos.y];
        this.delta = this.currentDelta();

        var dim = MochiKit.DOM.elementDimensions(this.element);
        
        this.dimensions = [0, 0];
        this.borders = [0, 0];
                        
        this.dimensions[0] = parseInt(MochiKit.Style.getStyle(this.element, 'width')) || 0;
        this.dimensions[1] = parseInt(MochiKit.Style.getStyle(this.element, 'height')) || 0;
        
        this.borders[0] = dim.w - this.dimensions[0];
        this.borders[1] = dim.h - this.dimensions[1];

        MochiKit.DragAndDrop.Resizables.activate(this);
        event.stop();
    },

    /** @id MochiKit.DragAndDrop.startDrag */
    startDrag: function (event) {
        this.dragging = true;
        if (this.options.selectclass) {
            MochiKit.DOM.addElementClass(this.element,
                                         this.options.selectclass);
        }
        if (this.options.zindex) {
            this.originalZ = parseInt(MochiKit.Style.getStyle(this.element,
                                      'z-index') || '0');
            this.element.style.zIndex = this.options.zindex;
        }

        if (this.options.ghosting) {
            this._clone = this.element.cloneNode(true);
            this.ghostPosition = MochiKit.Position.absolutize(this.element);
            this.element.parentNode.insertBefore(this._clone, this.element);
        }

        if (this.options.scroll) {
            if (this.options.scroll == window) {
                var where = this._getWindowScroll(this.options.scroll);
                this.originalScrollLeft = where.left;
                this.originalScrollTop = where.top;
            } else {
                this.originalScrollLeft = this.options.scroll.scrollLeft;
                this.originalScrollTop = this.options.scroll.scrollTop;
            }
        }

        MochiKit.DragAndDrop.Resizables.notify('start', this, event);
        if (this.options.starteffect) {
            this.options.starteffect(this.element);
        }
    },

    /** @id MochiKit.DragAndDrop.updateDrag */
    updateDrag: function (event, pointer) {
        if (!this.dragging) {
            this.startDrag(event);
        }
        MochiKit.Position.prepare();
        MochiKit.DragAndDrop.Resizables.notify('drag', this, event);
        this.draw(pointer);
        this.options.onchange(this);

        if (this.options.scroll) {
            this.stopScrolling();
            var p, q;
            if (this.options.scroll == window) {
                var s = this._getWindowScroll(this.options.scroll);
                p = new MochiKit.Style.Coordinates(s.left, s.top);
                q = new MochiKit.Style.Coordinates(s.left + s.width,
                                                   s.top + s.height);
            } else {
                p = MochiKit.Position.page(this.options.scroll);
                p.x += this.options.scroll.scrollLeft;
                p.y += this.options.scroll.scrollTop;
                p.x += (window.pageXOffset || document.documentElement.scrollLeft || document.body.scrollLeft || 0);
                p.y += (window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop || 0);
                q = new MochiKit.Style.Coordinates(p.x + this.options.scroll.offsetWidth,
                                                   p.y + this.options.scroll.offsetHeight);
            }
            var speed = [0, 0];
            if (pointer.page.x > (q.x - this.options.scrollSensitivity)) {
                speed[0] = pointer.page.x - (q.x - this.options.scrollSensitivity);
            } else if (pointer.page.x < (p.x + this.options.scrollSensitivity)) {
                speed[0] = pointer.page.x - (p.x + this.options.scrollSensitivity);
            }
            if (pointer.page.y > (q.y - this.options.scrollSensitivity)) {
                speed[1] = pointer.page.y - (q.y - this.options.scrollSensitivity);
            } else if (pointer.page.y < (p.y + this.options.scrollSensitivity)) {
                speed[1] = pointer.page.y - (p.y + this.options.scrollSensitivity);
            }
            this.startScrolling(speed);
        }

        // fix AppleWebKit rendering
        if (/AppleWebKit/.test(navigator.appVersion)) {
            window.scrollBy(0, 0);
        }
        event.stop();
    },

    /** @id MochiKit.DragAndDrop.finishDrag */
    finishDrag: function (event, success) {
        var dr = MochiKit.DragAndDrop;
        this.dragging = false;
        if (this.options.selectclass) {
            MochiKit.DOM.removeElementClass(this.element,
                                            this.options.selectclass);
        }

        if (this.options.ghosting) {
            // XXX: from a user point of view, it would be better to remove
            // the node only *after* the MochiKit.Visual.Move end when used
            // with revert.
            MochiKit.Position.relativize(this.element, this.ghostPosition);
            MochiKit.DOM.removeElement(this._clone);
            this._clone = null;
        }

        dr.Resizables.notify('end', this, event);

        var revert = this.options.revert;
        if (revert && typeof(revert) == 'function') {
            revert = revert(this.element);
        }

        var d = this.currentDelta();
        if (revert && this.options.reverteffect) {
            this._revert = this.options.reverteffect(this.element,
                d[1] - this.delta[1], d[0] - this.delta[0]);
        } else {
            this.delta = d;
        }

        if (this.options.zindex) {
            this.element.style.zIndex = this.originalZ;
        }

        if (this.options.endeffect) {
            this.options.endeffect(this.element);
        }

        dr.Resizables.deactivate();
    },

    /** @id MochiKit.DragAndDrop.keyPress */
    keyPress: function (event) {
        if (event.key().string != "KEY_ESCAPE") {
            return;
        }
        this.finishDrag(event, false);
        event.stop();
    },

    /** @id MochiKit.DragAndDrop.endDrag */
    endDrag: function (event) {
        if (!this.dragging) {
            return;
        }
        this.stopScrolling();
        this.finishDrag(event, true);
        event.stop();
    },

    /** @id MochiKit.DragAndDrop.draw */
    draw: function (point) {
        var pos = MochiKit.Position.cumulativeOffset(this.element);
        var d = this.currentDelta();
        pos.x -= d[0];
        pos.y -= d[1];

        if (this.options.scroll && (this.options.scroll != window && this._isScrollChild)) {
            pos.x -= this.options.scroll.scrollLeft - this.originalScrollLeft;
            pos.y -= this.options.scroll.scrollTop - this.originalScrollTop;
        }

        var p = [point.page.x - pos.x - this.offset[0],
                 point.page.y - pos.y - this.offset[1]];

        if (this.options.snap) {
            if (typeof(this.options.snap) == 'function') {
                p = this.options.snap(p[0], p[1]);
            } else {
                if (this.options.snap instanceof Array) {
                    var i = -1;
                    p = MochiKit.Base.map(MochiKit.Base.bind(function (v) {
                            i += 1;
                            return Math.round(v/this.options.snap[i]) *
                                   this.options.snap[i];
                        }, this), p);
                } else {
                    p = MochiKit.Base.map(MochiKit.Base.bind(function (v) {
                        return Math.round(v/this.options.snap) *
                               this.options.snap;
                        }, this), p);
                }
            }
        }

        var w = this.dimensions[0] + (p[0] - this.delta[0]);
        var h = this.dimensions[1] + (p[1] - this.delta[1]);

        if (this.options.min) {
            w = Math.max(w, this.options.min[0]);
            h = Math.max(h, this.options.min[1]);
        }
        
        if (this.options.max) {
            w = Math.min(w, this.options.max[0]);
            h = Math.min(h, this.options.max[1]);
        }
        
        var style = this.element.style;
        if ((!this.options.constraint) ||
            (this.options.constraint == 'horizontal')) {
            style.width = w + 'px';
        }
        if ((!this.options.constraint) ||
            (this.options.constraint == 'vertical')) {
            style.height = h + 'px';
        }
        if (style.visibility == 'hidden') {
            style.visibility = '';  // fix gecko rendering
        }
    },

    /** @id MochiKit.DragAndDrop.stopScrolling */
    stopScrolling: function () {
        if (this.scrollInterval) {
            clearInterval(this.scrollInterval);
            this.scrollInterval = null;
            MochiKit.DragAndDrop.Resizables._lastScrollPointer = null;
        }
    },

    /** @id MochiKit.DragAndDrop.startScrolling */
    startScrolling: function (speed) {
        if (!speed[0] && !speed[1]) {
            return;
        }
        this.scrollSpeed = [speed[0] * this.options.scrollSpeed,
                            speed[1] * this.options.scrollSpeed];
        this.lastScrolled = new Date();
        this.scrollInterval = setInterval(MochiKit.Base.bind(this.scroll, this), 10);
    },

    /** @id MochiKit.DragAndDrop.scroll */
    scroll: function () {
        var current = new Date();
        var delta = current - this.lastScrolled;
        this.lastScrolled = current;

        if (this.options.scroll == window) {
            var s = this._getWindowScroll(this.options.scroll);
            if (this.scrollSpeed[0] || this.scrollSpeed[1]) {
                var dm = delta / 1000;
                this.options.scroll.scrollTo(s.left + dm * this.scrollSpeed[0],
                                             s.top + dm * this.scrollSpeed[1]);
            }
        } else {
            this.options.scroll.scrollLeft += this.scrollSpeed[0] * delta / 1000;
            this.options.scroll.scrollTop += this.scrollSpeed[1] * delta / 1000;
        }

        var d = MochiKit.DragAndDrop;

        MochiKit.Position.prepare();
        d.Resizables.notify('drag', this);
        if (this._isScrollChild) {
            d.Resizables._lastScrollPointer = d.Resizables._lastScrollPointer || d.Resizables._lastPointer;
            d.Resizables._lastScrollPointer.x += this.scrollSpeed[0] * delta / 1000;
            d.Resizables._lastScrollPointer.y += this.scrollSpeed[1] * delta / 1000;
            if (d.Resizables._lastScrollPointer.x < 0) {
                d.Resizables._lastScrollPointer.x = 0;
            }
            if (d.Resizables._lastScrollPointer.y < 0) {
                d.Resizables._lastScrollPointer.y = 0;
            }
            this.draw(d.Resizables._lastScrollPointer);
        }

        this.options.onchange(this);
    },

    _getWindowScroll: function (win) {
        var vp, w, h;
        MochiKit.DOM.withWindow(win, function () {
            vp = MochiKit.Style.getViewportPosition(win.document);
        });
        if (win.innerWidth) {
            w = win.innerWidth;
            h = win.innerHeight;
        } else if (win.document.documentElement && win.document.documentElement.clientWidth) {
            w = win.document.documentElement.clientWidth;
            h = win.document.documentElement.clientHeight;
        } else {
            w = win.document.body.offsetWidth;
            h = win.document.body.offsetHeight;
        }
        return {top: vp.y, left: vp.x, width: w, height: h};
    },

    /** @id MochiKit.DragAndDrop.repr */
    repr: function () {
        return '[' + this.__class__.NAME + ", options:" + MochiKit.Base.repr(this.options) + "]";
    }
};

