import wizard
from osv import fields, osv
import urllib
import urllib2
from urllib import urlopen, urlencode, unquote
from urllib2 import build_opener
from BeautifulSoup import BeautifulSoup
import pooler
import re

#def get_lang(self,cr,uid,data):
#    
#    lang =[]
#    lang_obj = pooler.get_pool(cr.dbname).get('res.lang')
#    lang_search=lang_obj.search(cr,uid,[])
#    language = lang_obj.browse(cr,uid,lang_search)
#    for l in language:
#        lang.append((l.name, l.name ))
#    return lang

#add_form = '''<?xml version="1.0"?>
#<form string="Enter text">
#    <separator colspan="2" string="Enter Text and Select Destination Language"/>
#    <newline/>
#     <field name="text_1"/>
#     <field name="out_lang"/>
#     <newline/>
#     <separator colspan="2" string="Your translated text is here "/>
#     <newline/>
#     <field name="text_2"/>
#</form>'''
#
#add_fields = {
#       'text_1' :{'string':"Enter specialization",'type':'char', 'size': 256},
#       'out_lang' :{'string':"Select Language",'type':'selection', 'selection':get_lang},
#       'text_2' :{'string':"Enter specialization",'type':'char', 'size': 256, 'readonly':True}
#                 }

start_form = '''<?xml version="1.0"?>
    <form string=" " colspan="4">
     <newline/>
        <label string="To start Translation Press 'Translate'" align="0.0" colspan="3"/>
         <newline/>
         </form>
         '''
         
start_fields = { }

end_form = '''<?xml version="1.0"?>
    <form string=" " colspan="4">
     <newline/>
        <label string="Translation done..!!!" align="0.0" colspan="3"/>
         <newline/>
         </form>
         '''
end_fields = { }



def setUserAgent(userAgent):
    urllib.FancyURLopener.version = userAgent
    pass

def translate(self,cr,uid,data,context):
    print id,context
    pool = pooler.get_pool(cr.dbname)
    translation_obj=pool.get('ir.translation').browse(cr, uid,data['id'], context)
    print translation_obj['lang']
    in_lang=context['lang'][:2].lower().encode('utf-8')
    out_lang= translation_obj['lang'][:2].lower().encode('utf-8')
    
    print out_lang
    src=translation_obj['src'].encode('utf-8')
    setUserAgent("Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008070400 SUSE/3.0.1-0.1 Firefox/3.0.1")
    try:
        post_params = urllib.urlencode({"langpair":"%s|%s" %(in_lang,out_lang), "text":src,"ie":"UTF8", "oe":"UTF8"})
    except KeyError, error:
        print "Currently we do not support %s" %(error.args[0])
        return
    page = urllib.urlopen("http://translate.google.com/translate_t", post_params)
    content = page.read()
    page.close()
    match = re.search("<div id=result_box dir=\"ltr\">(.*?)</div>", content)
    value = match.groups()[0]
    print value
    
    pool.get('ir.translation').write(cr, uid, data['id'],{'value':value})
    return {}

class Transaltor(wizard.interface):
    states = {
            'init': {
             'actions': [],
                'result': {'type': 'form', 'arch':start_form, 'fields':start_fields, 'state':[('end','Cancel','gtk-cancel'),('translate','Translate','gtk-ok')]}
                },
            
            
            'translate': {
                'actions': [translate],
                'result': {'type': 'form', 'arch':end_form, 'fields':end_fields, 'state':[('end','OK','gtk-ok')]}
                },
            }
    
Transaltor('trans_wizard')            