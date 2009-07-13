
var ModalBox = function(options) {
    this.__init__(options);
}

ModalBox.prototype = {

    __init__ : function(options) {
        
        this.options = MochiKit.Base.update({
            title: 'Modalbox',  // title
            content: null,      // content
            buttons: []        // buttons
        }, options || {});
		
        if (MochiKit.DOM.getElement('modalbox_overlay')){
            throw "Only one Modalbox instance is allowed per page.";
        }

        this.title = DIV({'class': 'modalbox-title'}, this.options.title);
        this.content = DIV({'class': 'modalbox-content'}, this.options.content || '');
        
        var btnCancel = BUTTON({'class': 'button', 'type': 'button'}, 'Cancel');
        MochiKit.Signal.connect(btnCancel, 'onclick', this, this.hide);

        var buttons = MochiKit.Base.map(function(btn){
            var b = MochiKit.DOM.BUTTON({'class': 'button', 'type': 'button'}, btn.text);
            MochiKit.Signal.connect(b, 'onclick', btn.onclick || MochiKit.Base.noop);
            return b;
        }, this.options.buttons || []);

        buttons.push(btnCancel);

        var content = DIV(null,
                        this.title,
                        this.content,
                            TABLE({'class': 'modalbox-buttons', 'cellpadding': 2, 'width': '100%'}, 
                                TBODY(null, 
                                    TR(null,
                                        TD({'align': 'right', 'width': '100%'}, buttons)))));
        
        this.overlay = DIV({id: 'modalbox_overlay'});
        MochiKit.DOM.appendChildNodes(document.body, this.overlay);
        MochiKit.Style.setOpacity(this.overlay, 0.7);
    
        this.box = DIV({id: 'modalbox'});
        MochiKit.DOM.appendChildNodes(document.body, this.box);        
        MochiKit.DOM.appendChildNodes(this.box, content);
    },

    show : function() {

        setElementDimensions(this.overlay, elementDimensions(document.body));
//        MochiKit.DOM.setElementDimensions(this.overlay, {'w': window.screen.availWidth, 'h': window.screen.availHeight});
		
        var w = this.width || 0;
        var h = this.height || 0;
		
        MochiKit.DOM.setElementDimensions(this.box, {w: w, h: h});
		
        var vdh = window.innerHeight || window.screen.availHeight;
        var vdw = window.innerWidth || window.screen.availWidth;
     
        var md = this.box.clientHeight;
        var x = (vdw / 2) - (w / 2);
        var y = (vdh / 2) - (h / 2);
        
        x = Math.max(0, x);
        y = Math.max(0, y);
        
        y = y + document.documentElement.scrollTop;
        setElementPosition(this.box, {x: x, y: y});

        showElement(this.overlay);
        showElement(this.box);

        // set the height of content
        var h2 = h - getElementDimensions(this.title).h - 
            getElementDimensions(getElementsByTagAndClassName('table', 'modalbox-buttons', this.box)[0]).h;

        setElementDimensions(this.content, {h: h2});

        MochiKit.Signal.signal(this, "show", this);
    },

    hide : function() {
        hideElement(this.box);
        hideElement(this.overlay);

        MochiKit.Signal.signal(this, "hide", this);
    }
}

// vim: sts=4 st=4 et
