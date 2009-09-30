import pooler
import base64

__description__ = """This plugin generate URL
    url : which defines url
    text_display : defines the text which one want to display on url 
    one can add more arguments which one wants to add as key=value pair in url
"""

__args__ = [('url','string'),('text_display','string')]

def php_url(cr,uid,**plugin_args):
    res =[]
    arguments = ''
    arg = ('url','text_display','encode')
    url_arg = filter(lambda x : x not in arg,plugin_args)
    for a in url_arg:
        if arguments =='' :
            arguments  += '%s=%s'%(a,plugin_args[a])
        else :
            arguments  += '&%s=%s'%(a,plugin_args[a])
    if 'encode' in plugin_args and plugin_args['encode'] : 
        arguments = base64.encodestring(arguments)
    url_name = plugin_args['url'] or ''
    if url_name.find('http://')<0:
        url_name = 'http://' + url_name
        if arguments :
            url_name = url_name+"?data="+ arguments
    value = "<a href= '" + url_name + "' target='_blank'>" + plugin_args['text_display'] + "</a>"
    return value
#    return (url_name,plugin_args['text_display'])

#vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
