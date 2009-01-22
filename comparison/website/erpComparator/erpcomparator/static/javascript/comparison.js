//function selection(id) {
//	var elem = document.getElementById(id);
//    elem.style.display = '';
//}
//
//function open_comparison(id) {
//	var elem = document.getElementById(id);
//    elem.style.display = elem.style.display == 'none' ? '' : 'none';
//}
//
//function close_comparison(id) {
//	var elem = document.getElementById(id);
//    elem.style.display = 'none';
//}


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

function change_vote(id) {
	openWindow(getURL('/comparison/voting', {id: id}), {width: 500, height: 350});
}

function open_item_vote(id, header) {
	
	params = [];
	params['id'] = id;
	params['header'] = header;
	
	var req = Ajax.post('/comparison/item_voting', params);
	
	req.addCallback(function(xmlHttp){
		var d = window.mbox.content;
		d.innerHTML = xmlHttp.responseText;
		
		window.mbox.width = 500;
        window.mbox.height = 340;
        
        window.mbox.onUpdate = item_vote;
		window.mbox.show();
	});
}

var onUpdate = function(){
    window.mbox.onUpdate();
}

MochiKit.DOM.addLoadEvent(function(evt){

    window.mbox = new ModalBox({
        title: 'Voting...',
        buttons: [
            {text: 'Save', onclick: onUpdate},
        ]
    });

});

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
	
	/*
	params['id'] = $('id').value;
	params['score_id'] = $('score_id').value;
	params['item_id'] = $('item_id').value;
	params['note'] = $('note').value;
	
	var req = Ajax.JSON.post('/comparison/update_item_voting', params);
    req.addCallback(function(obj){
    	if(obj.res) {
    		window.mbox.hide();
    		treenode.update();
    		
    	}
    	if (obj.error) {
            return alert(obj.error);
        }
    });
	
	
	*/
}