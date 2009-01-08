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

function on_button_click() {
	openWindow('/login/');
	
}