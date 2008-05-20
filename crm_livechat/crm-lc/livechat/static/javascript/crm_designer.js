function popup_table(url)
{
	window.open(url,'welcome','width=450,height=300,resizable=yes,scrollbars=yes')

}

function refreshg()
{
	tosend = document.getElementsByName('txtarea').value
	var params = {}
	var req = Ajax.JSON.post('/chatfunc/chatbox2', params);
	//var req = Ajax.JSON.post('/justsend', params);
	a = req.addCallback(function(obj){
				msgs= obj.msglist;
				a = MochiKit.DOM.getElement('refreshdiv');
				a.innerHTML=''

				dlid = MochiKit.DOM.DIV({});
				for(i=0;i<msgs.length;i++)
				{
					dtid = MochiKit.DOM.DIV({});
					dtid.innerHTML = msgs[i][0];
					if(msgs[i][1] == 'sender')
						dtid.style.color = '#AA1E09';
					else
						dtid.style.color = '#204A87';

					MochiKit.DOM.appendChildNodes(dlid,dtid);
				}
				MochiKit.DOM.appendChildNodes(a,dlid);
				a.scrollTop = a.scrollHeight;
            });
      return 1;

}

function close_chat(thisid)
{
	var params = {'close':'close'}
	var req = MochiKit.Async.doSimpleXMLHttpRequest('/chatfunc/close_chat', params);
	//var req = Ajax.JSON.post('/justsend', params);
	a = req.addCallback(function(obj){
				thisid.close();

            });
      return 1;

}

function activate_refreshg()
{
	kintervalId = setInterval ( "refreshg()", 1000 );
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