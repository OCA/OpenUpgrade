///////////////////////////////////////////////////////////////////////////////
//
// Copyright (c) 2007 TinyERP Pvt Ltd. (http://tinyerp.com) All Rights Reserved.
//
// $Id: ajax.js 1327 2007-12-06 08:51:47Z ame $
//
// WARNING: This program as such is intended to be used by professional
// programmers who take the whole responsability of assessing all potential
// consequences resulting from its eventual inadequacies and bugs
// End users who are looking for a ready-to-use solution with commercial
// garantees and support are strongly adviced to contract a Free Software
// Service Company
//
// This program is Free Software; you can redistribute it and/or
// modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
//
///////////////////////////////////////////////////////////////////////////////

var Ajax = function(){
}

Ajax.COUNT = 0;

Ajax.prototype = {

    get: function(url, params){

        Ajax.COUNT += 1;

        var req = MochiKit.Async.doSimpleXMLHttpRequest(url, params);

        return req.addBoth(function(xmlHttp){
            Ajax.COUNT -= 1;
            return xmlHttp;
        });
    },

    post: function(url, params){

        Ajax.COUNT += 1;

        var req = MochiKit.Async.getXMLHttpRequest();
        req.open("POST", url, true);

        req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        req.setRequestHeader("Connection", "close");

        var qs = null;

        if (params) {
            qs = MochiKit.Base.queryString(params);
            req.setRequestHeader("Content-length", qs.length);
        }

        req = MochiKit.Async.sendXMLHttpRequest(req, qs);

        return req.addBoth(function(xmlHttp){
            Ajax.COUNT -= 1;
            return xmlHttp;
        });
    }
}

Ajax.get = function(url, params){
    return new Ajax().get(url, params);
}

Ajax.post = function(url, params){
    return new Ajax().post(url, params);
}

var JSON = function(){
}

JSON.prototype = {

    get: function(url, params){
        var req = Ajax.get(url, params);
        return req.addCallback(MochiKit.Async.evalJSONRequest);
    },

    post: function(url, params){
        var req = Ajax.post(url, params);
        return req.addCallback(MochiKit.Async.evalJSONRequest);
    }
}

JSON.get = function(url, params){
    return new JSON().get(url, params);
}

JSON.post = function(url, params){
    return new JSON().post(url, params);
}

Ajax.JSON = new JSON();

// vim: sts=4 st=4 et
