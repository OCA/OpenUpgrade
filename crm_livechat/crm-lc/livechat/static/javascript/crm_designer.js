function popup_table(url)
{
	window.open(url,'welcome','width=450,height=260,resizable=yes,scrollbars=yes')
	
}
var refreshflag=false;
function startrec()
{

	refreshflag = true;
	refresh_iframe();
}

function quitrec()
{

	refreshflag = false;
}

function refresh_iframe()
{
	document.getElementById('msgframe').src = '/messageBox';
	if(refreshflag)
		{
		setTimeout('refresh_iframe()',1000);
		}
	else
		return 0;
}
