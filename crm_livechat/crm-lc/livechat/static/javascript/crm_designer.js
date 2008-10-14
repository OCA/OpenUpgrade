//var wn = 0;
//var ajax_counter = 0;
function popup_table(url)
{
	window.open( url,'welcome','width=450,height=300,resizable=yes,scrollbars=yes')
}

function refreshg()
{
	if (!chatendflag)
	{
	var params = {}
	var req = Ajax.JSON.post('/chatfunc/chatbox2', params);
	a = req.addCallback(function(obj){
//				closechat = obj.close_chat
				msgs= obj.msglist;
				a = MochiKit.DOM.getElement('refreshdiv');
				a.innerHTML=''
				dlid = MochiKit.DOM.DIV({});
				for(i=0;i<msgs.length;i++)
				{
//				if (msgs[i]['message'] == 'closechat')
//						close_chat(chatwindow);
					dtid = MochiKit.DOM.DIV({});
					senderpart = MochiKit.DOM.DIV({});
					senderpart.innerHTML = msgs[i]['sender'] + " : "
					senderpart.style.display = 'inline';
					if (msgs[i]['type'] != 'sender')
						senderpart.className = 'reciever';
					else
						senderpart.className = 'sender';
					MochiKit.DOM.appendChildNodes(dtid,senderpart);

					messagepart = MochiKit.DOM.DIV({});
					messagepart.style.display = 'inline';
					messagepart.className = 'message';
					messagepart.innerHTML = msgs[i]['message']
					MochiKit.DOM.appendChildNodes(dtid,messagepart);

					MochiKit.DOM.appendChildNodes(dlid,dtid);
				}
				MochiKit.DOM.appendChildNodes(a,dlid);
				a.scrollTop = a.scrollHeight;
            });
      return 1;
	}

}
var chatendflag = false;
function close_chat(thisid)
{
	thisid.close();
	chatendflag = true;
	var params = {'close':'close'}
//	if (ajax_counter = 0)
//	{
//		ajax_counter++;
	var req = MochiKit.Async.doSimpleXMLHttpRequest('/chatfunc/close_chat', params);
		//var req = Ajax.JSON.post('/justsend', params);
	a = req.addCallback(function(obj){
					chatendflag = false;
	            });
      return 1;
}

var kintervalId=0;
function activate_refreshg(thisid)
{
	if(chatendflag && kintervalId!=0)
		clearInterval(kintervalId)
	else{
		kintervalId = 0;
		kintervalId = setInterval ( "refreshg()", 1000 );
	}
}

function topicsel(id)
{
	var actionurl = "/chatfunc/start_chat/";
	var params = {'topicid':id}
	var req = Ajax.JSON.post(actionurl, params);
	a = req.addCallback(function(obj){
				if(obj.message == 'Active')
					popup_table("/chatfunc/chat_window");
				else
					alert(obj.message);
            });
    return 1;
}

function sendmsg()
{
	txtnode = MochiKit.DOM.getElement('text2')
	txt= txtnode.value;
	var actionurl = "/chatfunc/justsend/";
	var params = {'messg': txt};
	var req = Ajax.JSON.post(actionurl, params);
	a = req.addCallback(function(obj){
					txtnode.value = '';
            });
    return 1;


}

function submitenter(myfield,e)
{
	var keycode;
	if (window.event) keycode = window.event.keyCode;
	else if (e) keycode = e.which;
	else return true;

	if (keycode == 13)
   	{
   		//myfield.form.submit();
   		sendmsg();
   		return false;
   	}
	else
   		return true;
}

function getWindowHeight() {
	var windowHeight = 0;
	if (typeof(window.innerHeight) == 'number')
	{
		windowHeight = window.innerHeight;
	}
	else
	{
		if (document.documentElement && document.documentElement.clientHeight)
		{
			windowHeight = document.documentElement.clientHeight;
		}
		else
		{
			if (document.body && document.body.clientHeight)
			{
				windowHeight = document.body.clientHeight;
			}
		}
	}
	window.scrollTo = windowHeight;
	return windowHeight;
}

function setWrap()
{
	if (document.getElementById)
	{
		var windowHeight = getWindowHeight();

		if (windowHeight > 0)
		{
			var wrapElement = el('wrap');
			wrapElement.style.position = 'absolute';
			wrapHeight = (windowHeight-70);
			wrapElement.style.height = wrapHeight+'px';
			wrap80 = (wrapHeight -(Math.round(wrapHeight*0.20)))-20
			wrap20 = (wrapHeight -(Math.round(wrapHeight*0.80)))-20
			//alert(wrapHeight+":"+wrap80+":"+wrap10);
			el('trref').style.height = (wrapHeight-25-50) +'px';
			el('refreshdiv').style.height = (wrapHeight-25-50)+'px';
			el('buttonref').style.height = '25px';
			el('txtarearef').style.height = '50px';
			el('text2').style.height = '50px';
		}
	}
}

function el(id)
{
	return document.getElementById(id);
}
