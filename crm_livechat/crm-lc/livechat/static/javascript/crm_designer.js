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
				alert("successfully rec"+obj.msglist);
            });
      return 1;		
	
}

function call_send()
{	
	tosend = document.getElementsByName('txtarea').value
	var params = {'msg':tosend}
	var req = MochiKit.Async.doSimpleXMLHttpRequest('/chatfunc/justsend', params);	
	//var req = Ajax.JSON.post('/justsend', params);
	a = req.addCallback(function(obj){
				alert("successfully sent");
				
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

function topicsel(id)
{
	var actionurl = "/chatfunc/start_chat/"+id;
//	document.getElementById("topic_form").action = actionurl;
//	alert(actionurl+"--------"+document.getElementById("topic_form").action);
	popup_table(actionurl);
}