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

function item_vote(id, header) {
	openWindow(getURL('/comparison/item_voting', {id: id, header: header}), {width: 500, height: 350});
}