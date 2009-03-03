
function radarData() {
	ids = getSelectedItems_graph();
	ids = map(function(r){return r.id;}, ids);
	ids = '[' + ids.join(', ') + ']';
	return ids
}

function getSelectedItems_graph() {
	tbl = document.getElementById('graph_item_list');
	return filter(function(box){
		if (box.checked) {
        	return box.id;
       	}
	}, getElementsByTagAndClassName('input', 'grid-record-selector', tbl));
}

function getRecords() {
	ids = getSelectedItems();
	ids = map(function(r){return r.id;}, ids);
	ids = '[' + ids.join(', ') + ']';
	window.location.href = '/comparison?ids=' + ids;
}

function getSelectedRecords() {
	return map(function(box){
    	return box.value;
	}, this.getSelectedItems());
}

function getSelectedItems() {
	tbl = document.getElementById('item_list');
	return filter(function(box){
		if (box.checked) {
        	return box.id;
       	}
	}, getElementsByTagAndClassName('input', 'grid-record-selector', tbl));
}

function do_login(user_name, password) {
	params = {};
	if('undefined' == typeof user_name && 'undefined' == typeof password) {
		params['user_name'] = $('user_name').value;
		params['password'] = $('password').value;
	}
	else {
		params['user_name'] = user_name;
		params['password'] = password;
	}

	var req = Ajax.JSON.post('/login/check_login', params);
	req.addCallback(function(obj){
		if (obj.user_info) {
			window.location.href = '/comparison';
		}
		if (obj.error) {
			return alert(obj.error);
		}
	});
}

function register(msg) {
	
	if('undefined' != typeof msg) {
		var params = {}
		params["msg"] = msg;
	}
	else {
		var params = {}
	}
	var req = Ajax.post('/login/', params)
	req.addCallback(function(xmlHttp) {
			var d = window.mbox.content;
			d.innerHTML = xmlHttp.responseText;
			
			window.mbox.width = 500;
	        window.mbox.height = 330;
	        
	        window.mbox.onUpdate = add_new_user;
			window.mbox.show();
			});
}

function add_new_user() {
	if($('registered_user') && $('registered_user').checked) {
		do_login($('usr_name').value, $('usr_password').value)
	}
	else {
	params = {}
	params['user_name'] = $('name_user').value;
	params['password'] = $('passwd').value;
	params['email'] = $('email').value;
	
	name = params['user_name'].match(/^[A-Za-z0-9_]+$/);
	if (! name) {
		return alert("Username accepts only Digit, Later, _ sign...");	
	}
	
	if (!params['user_name'] || !params['password'] || !params['email']) {
		return alert("Fields marked with * are mandatory...");
	}
	
	var req = Ajax.JSON.post('/login/do_login', params);
	req.addCallback(function(obj){
		if (obj.res) {
			window.mbox.hide();
			window.location.href = '/comparison';
		}
		if (obj.error) {
			return alert(obj.error);
		}
	});
	}
}

function change_vote(node, pond_val) {
	
	params = {}
	params['id'] = node.name;
	params['pond_val'] = pond_val;
	
	var req = Ajax.JSON.post('/comparison/voting', params);
	req.addCallback(function(obj){
		if (obj.value) {
			node.update();
		}
		if (obj.error) {
            return alert(obj.error);
        }
	});
}

function view_graph(id) {
	window.location.href = '/graph?view_id=' + id;
}

function add_factor(id) {
	params = {};
	
	params['id'] = id;
	var req = Ajax.post('/comparison/add_factor', params);
	req.addCallback(function(xmlHttp) {
		
		var d = window.mbox.content;
		d.innerHTML = xmlHttp.responseText;
		
		if(getElement('error_box') != null) {
        	var msg = "You are not logged in..."
        	register(msg);
        }
        
        else {
		window.mbox.width = 500;
        window.mbox.height = 330;
        
        window.mbox.onUpdate = add_new_factor;
		window.mbox.show();
        }
	});
}

function add_new_factor() {
	treenode = comparison_tree.selection_last;
	params = {};
	
	params['model'] = 'comparison.factor';
	params['factor_id'] = $('factor_id').value;
	params['parent_name'] = $('parent_name').value;
	params['parent_id'] = $('parent_id').value;
	params['ponderation'] = $('ponderation').value;
	params['ftype'] = $('type').value;
	
	params['ids'] = [];
	params['fields'] = [];
	
	if (!params['factor_id']) {
		return alert("Fields marked with * are mandatory...");
	}
	else {
		var req = Ajax.JSON.post('/comparison/data', params);
	    req.addCallback(function(obj){
	    	if(obj.records) {
	    		window.mbox.hide();
	    		try {
	    			var node = comparison_tree.createNode(obj.records[0]);
	        		treenode.appendChild(node);
	    		}
	        	catch(e) {
	        		alert(e);
	        	}
	    	}
	    	if (obj.error) {
//	            return alert(obj.error);
	            register()
	        }
	    });
	}
}

var onUpdate = function(){
    window.mbox.onUpdate();
}

MochiKit.DOM.addLoadEvent(function(evt){

    window.mbox = new ModalBox({
        title: 'Evaluation Matrix...',
        buttons: [
            {text: 'Submit', onclick: onUpdate}
        ]
    });
});

function open_item_vote(id, header) {
	
	params = {};
	params['id'] = id;
	params['header'] = header;
	
	var req = Ajax.post('/comparison/item_voting', params);
	
	req.addCallback(function(xmlHttp){
		var d = window.mbox.content;
		d.innerHTML = xmlHttp.responseText;
		
        if(getElement('error_box') != null) {
        	var msg = "You are not logged in..."
        	register(msg);
        }
        else {
        	window.mbox.width = 500;
        	window.mbox.height = 330;
        	window.mbox.onUpdate = item_vote;
			window.mbox.show();
        }
	});
}

function item_vote() {
	
	var treenode = comparison_tree.selection_last;
	var childnodes = treenode.childNodes; 
	window.mbox.hide();
	var i = 1;
	var val = '';
	
	forEach(treenode.childNodes, function(node){
		var name = node.record.id;
		try{
			var elem = document.getElementById(name + '_score_id');
		}
		catch(e) {
			alert(e)
		}
		
		if(elem != null) {
			var params = {};
			params['id'] = name;
			params['score_id'] = $(name + '_score_id').value;
			params['item_id'] = $('item_id').value;
			params['note'] = $('note').value;
			values = "id,"+name+"|score_id,"+$(name + '_score_id').value+"|item_id,"+$('item_id').value+"|note,"+$('note').value;
		}
		
		if (i != treenode.childNodes.length) {
			val += values + '!';
			i++;
		}
		else {
			val += values;
		}
	});
	
	var req = Ajax.JSON.post('/comparison/update_item_voting?_terp_values='+val);
    req.addCallback(function(obj){
    	if(obj.res) {
    		forEach(childnodes, function(node){
    			node.update();
    		});
    		while (treenode && treenode.parentNode) {
				treenode.update();
				treenode = treenode.parentNode;
			}
		}
    	if (obj.error) {
            return alert(obj.error);
//				register()
        }
    });
	
}
function load_radar() {
	var browserName = navigator.appName;
	var browserVersion = parseInt(navigator.appVersion);
	ids = radarData();
	
	if(browserName.indexOf('Netscape')!=-1 && browserVersion >= 4) {
		factor_name= $('factors').value;
		factor_name = factor_name.replace(/&/g, "@") ;
	}
	
	else if(browserName.indexOf('Microsoft Internet Explorer')!=-1 && browserVersion>=3) {
		MochiKit.DOM.getElementsByTagAndClassName('select','factors', null)[0].parentNode.parentNode.cells[0].style.padding = '10px';
		var index = MochiKit.DOM.getElementsByTagAndClassName('select','factors', null)[0].selectedIndex;
		var factor = MochiKit.DOM.getElementsByTagAndClassName('select','factors', null)[0][index].innerHTML;
		factor_name= factor;
		factor_name = factor_name.replace(/&amp;/g, "@") ;
	}
	
	else if(browserName.indexOf('Opera')!=-1) {
		log("Opera")
	}
	
	list = urlEncode('/graph/radar?ids='+ids+'&factor_name='+factor_name);
	
	swfobject.embedSWF("/static/open-flash-chart.swf", "radar_chart", "700", "700",
						"9.0.0", "expressInstall.swf", {'data-file': list});
}

function load_planet() {
	params = {}
	var req = Ajax.post('/static/planet_comparison/me-meta/output/index.html', params);
	
	req.addCallback(function(xmlHttp){
		div = $('load_planet');
		div.innerHTML = xmlHttp.responseText;
	});
}

function on_button_click(evt, node) {
	if (evt.src().name == 'show_graph') {
		view_graph(node.name);
	}
	else if (evt.src().name == 'add_factor') {
		add_factor(node.name);
	}
	else if (evt.src().name == 'incr') {
		change_vote(node, 'incr');
	}
	else if (evt.src().name == 'decr') {
		change_vote(node, 'decr');
	}
	
}

var expand_tree = function(elem) {
	if(elem.innerHTML == 'Complete Comparison') {
		elem.innerHTML = 'Summerized Comparison'
		window.location.href = '/comparison?all='+'1'
	}
	else if(elem.innerHTML = 'Summerized Comparison') {
		elem.innerHTML = 'Complete Comparison'
		window.location.href = '/comparison'
	}
}
