
function radarData() {
	ids = getSelectedItems();
	ids = map(function(r){return r.id;}, ids);
	ids = '[' + ids.join(', ') + ']';
	load_radar(ids);
}

function getSelectedItems() {
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

function change_vote(id, event) {
	
	treenode = comparison_tree.selection_last;
	if (treenode) {
		var req = Ajax.JSON.post('/comparison/voting', {id: id, event: event});
		req.addCallback(function(obj){
			if(obj.res) {
				treenode.update();
			}
			if (obj.error) {
	            return alert(obj.error);
	        }
		});
	}
}

function view_graph(id) {
	window.location.href = '/graph?id=' + id;
}

function add_factor(id) {
	params = [];
	
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
	params = [];
	
	params['model'] = 'comparison.factor';
	params['factor_id'] = $('factor_id').value;
	params['parent_name'] = $('parent_name').value;
	params['parent_id'] = $('parent_id').value;
	params['ponderation'] = $('ponderation').value;
	params['ftype'] = $('type').value;
	
	params['ids'] = [];
	params['fields'] = [];
	
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
	
	params = [];
	params['id'] = id;
	params['header'] = header;
	
	var req = Ajax.post('/comparison/item_voting', params);
	
	req.addCallback(function(xmlHttp){
		var d = window.mbox.content;
		d.innerHTML = xmlHttp.responseText;
		
		window.mbox.width = 600;
        window.mbox.height = 400;
        
        window.mbox.onUpdate = item_vote;
		window.mbox.show();
	});
}

function item_vote() {
	
	treenode = comparison_tree.selection_last;
	params = [];
	 
	child_ids = [];
	trs = getElementsByTagAndClassName('tr', 'factor_row');
	for (var i=0; i<trs.length; i++) {
		child_ids[i] = trs[i].id.split('_')[0];
	}
	
	forEach(child_ids, function(x){
		params['id'] = x;
		params['score_id'] = $(x + '_score_id').value;
		params['item_id'] = $('item_id').value;
		
		var req = Ajax.JSON.post('/comparison/update_item_voting', params);
	    req.addCallback(function(obj){
	    	if(obj.res) {
	    		window.mbox.hide();
	    		forEach(treenode.childNodes, function(y){
	    			y.update();
	    		});
	    		treenode.update();
	    		
	    	}
	    	if (obj.error) {
	            return alert(obj.error);
	        }
	    });
	});
}

function load_radar(ids) {
	
	factor_name= $('factors').value;
	factor_name = factor_name.replace(/&/, "@");
	
	list = urlEncode('/graph/radar?ids='+ids+'&factor_name='+factor_name);
	
	swfobject.embedSWF("/static/open-flash-chart.swf", "radar_chart", "700", "700",
						"9.0.0", "expressInstall.swf", {'data-file': list});
}

function on_radar_click(index){
	
	factor_name= $('factors').value;
	factor_name = factor_name.replace(/&/, "@");
	
	window.location.href = '/graph?factor_index='+index+'&parent_name='+factor_name;
}

function on_button_click(evt, node) {
	if (evt.src().name == 'show_graph') {
		view_graph(node.name);
	}
	if (evt.src().name == 'add_factor') {
		add_factor(node.name);
	}
}

