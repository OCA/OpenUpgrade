
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

function do_login() {
	user_name = $('user_name').value;
	password = $('password').value;
	
	login_list = '/comparison?user_name='+user_name+'&password='+password;
	window.location.href = login_list;
}

function register() {
	params = {}
	var req = Ajax.post('/login', params);
	req.addCallback(function(xmlHttp) {
		
		var d = window.mbox.content;
		d.innerHTML = xmlHttp.responseText;
		
		window.mbox.width = 400;
        window.mbox.height = 250;
        
        window.mbox.onUpdate = add_new_user;
		window.mbox.show();
	});
}

function add_new_user() {
	
	user_name = $('name_user').value;
	password = $('passwd').value;
	email = $('email').value;
	
	if (!user_name || !password || !email) {
		return alert("Fields marked with * are mandatory...");
	}
	else {
		window.location.href = '/login/do_login?user_name='+user_name+'&password='+password+'&email='+email;
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
		
		window.mbox.width = 450;
        window.mbox.height = 300;
        
        window.mbox.onUpdate = add_new_factor;
		window.mbox.show();
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
	            return alert(obj.error);
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
            {text: 'Save', onclick: onUpdate},
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
		
		window.mbox.width = 650;
        window.mbox.height = 500;
        
        window.mbox.onUpdate = item_vote;
		window.mbox.show();
	});
}

function item_vote() {
	
	var treenode = comparison_tree.selection_last;
	var childnodes = treenode.childNodes; 
		
	window.mbox.hide();
	var final_params = []
	var i = 1;
	var val = '';
	
	forEach(treenode.childNodes, function(node){
		var name = node.record.id;
		var params = {};
		params['id'] = name;
		params['score_id'] = $(name + '_score_id').value;
		params['item_id'] = $('item_id').value;
		params['note'] = $('note').value;
		
		values = "id,"+name+"|score_id,"+$(name + '_score_id').value+"|item_id,"+$('item_id').value+"|note,"+$('note').value;
		
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
				log("name.."+node.name);
			});
    		forEach(childnodes, function(node){
    			node.update();
    		});
		}
    	if (obj.error) {
            return alert(obj.error);
        }
    });
	
	while (treenode && treenode.parentNode) {
		treenode.update();
		treenode = treenode.parentNode;
	}
}
function load_radar() {
	
	ids = radarData();
	
	factor_name= $('factors').value;
	factor_name = factor_name.replace(/&/g, "@");
	
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

