import pooler
from pyDes import *
import base64

__description__ = """This plugin generate URL
    url : which defines url
    text_display : defines the text which one want to display on url 
    one can add more arguments which one wants to add as key=value pair in url
"""

__args__ = [('url','string'),('text_display','string')]

def php_url(cr,uid,customer_ids,**args):
    res =[]
    arguments = ''
    for a in args.keys() :
        if a!='url' and a!='text_display':
            if arguments =='' :
                arguments  += '%s=%s'%(a,args[a])
            else :
                arguments  += '&%s=%s'%(a,args[a])
    url_name = args['url']
    if url_name.find('http://')<0:
        url_name = 'http://' + url_name
        if arguments :
            url_name = url_name+"?"+ base64.encodestring(arguments)
    value = "<a href= '" + url_name + "' target='_blank'>" + args['text_display'] + "</a>"
    return value

#vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
