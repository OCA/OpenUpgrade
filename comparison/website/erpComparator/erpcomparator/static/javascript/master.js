
var getURL = function(path, args) {
    var qs = args ? queryString(args) : null;
    return qs ? path + "?" +  qs : path;
}

function validate_email(email) {
    var re  = /(^[a-z]([a-z_\.]*)@([a-z_\.]*)([.][a-z]{3})$)|(^[a-z]([a-z_\.]*)@([a-z_\.]*)(\.[a-z]{3})(\.[a-z]{2})*$)/i;
    return re.test(email);
}

function set_cookie(name, value) {
    document.cookie = name + "=" + escape(value) + "; path=/";
}

function get_cookie(name) {
    var dc = document.cookie;
    var prefix = name + "=";
    var begin = dc.indexOf("; " + prefix);
    if (begin == -1) {
        begin = dc.indexOf(prefix);
        if (begin != 0) return null;
    } else {
        begin += 2;
    }
    var end = document.cookie.indexOf(";", begin);
    if (end == -1) {
        end = dc.length;
    }
    return unescape(dc.substring(begin + prefix.length, end));
}

function openWindow(anchor, options) {

    var opts = MochiKit.Base.update({
        name        : 'win' + Math.round(Math.random()*100000),
        center      : true,
        x           : null,
        y           : null,
        width       : 800, //screen.availWidth - 200,
        height      : 600, //screen.availHeight - 200,
        scrollbars  : true,
        fullscreen  : false,
        menubar     : false,
        locationbar : false,
        resizable   : true
    }, options || {});

    //opts.width = opts.width > 0 ? opts.width : 800;
    //opts.height = opts.height > 0 ? opts.height : 600;

    var args = '';

    args += "height=" + (opts.fullscreen ? screen.availHeight : opts.height) + ",";
    args += "width=" + (opts.fullscreen ? screen.availWidth : opts.width) + ",";
    
    if (!opts.center) {
        opts.x = 0;
        opts.y = 0;
        args += "screenx=" + opts.x + ",";
        args += "screeny=" + opts.y + ",";
        args += "left=" + opts.x + ",";
        args += "top=" + opts.y + ",";
    }

    if (opts.center && !opts.fullscreen) {
        opts.y = Math.floor((screen.availHeight - opts.height - (screen.height - screen.availHeight)) / 2);
        opts.x = Math.floor((screen.availWidth - opts.width - (screen.width - screen.availWidth)) / 2);
        args += "screenx=" + opts.x + ",";
        args += "screeny=" + opts.y + ",";
        args += "left=" + opts.x + ",";
        args += "top=" + opts.y + ",";
    }

    if (opts.scrollbars) { args += "scrollbars=1,"; }
    if (opts.menubar) { args += "menubar=1,"; }
    if (opts.locationbar) { args += "location=1,"; }
    if (opts.resizable) { args += "resizable=1,"; }

    var win = window.open(anchor, opts.name, args);
    return false;

}

// browser information
window.browser = new Object;

// Internet Explorer
window.browser.isIE = /msie/.test(navigator.userAgent.toLowerCase());

// Internet Explorer 6
window.browser.isIE6 = /msie 6/.test(navigator.userAgent.toLowerCase());

// Internet Explorer 7
window.browser.isIE7 = /msie 7/.test(navigator.userAgent.toLowerCase());

// Gecko(Mozilla) derived
window.browser.isGecko = /gecko\//.test(navigator.userAgent.toLowerCase());
window.browser.isGecko18 = /rv:1.9.*gecko\//.test(navigator.userAgent.toLowerCase());
window.browser.isGecko19 = /rv:1.9.*gecko\//.test(navigator.userAgent.toLowerCase());

// Apple WebKit derived
window.browser.isWebKit = /webkit/.test(navigator.userAgent.toLowerCase());

// Opera
window.browser.isOpera = /opera/.test(navigator.userAgent.toLowerCase());

// vim: ts=4 sts=4 sw=4 si et

