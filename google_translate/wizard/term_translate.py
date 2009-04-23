# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import urllib
from urllib import urlopen, urlencode, unquote

import wizard
from osv import fields, osv
import pooler
import re

trans_form = '''<?xml version="1.0"?>
    <form string="Translation" colspan="4">
         <newline/>
         <label string="Translate Terms of tiny using google" align="0.0" colspan="3"/>
         <newline/>
     </form> '''
trans_fields = { }

trans_sum = '''<?xml version="1.0"?>
        <form string="Translation" colspan="4">
             <newline/>
             <label string="Successfullly Translate" />
             <newline/>
        </form> '''
trans_sum_fields = { }

def setUserAgent(userAgent):
    urllib.FancyURLopener.version = userAgent
    pass

def _translate(self, cr, uid, data, context={}):
    # Todo:
    #    1. should work for all language (arabic)
    #    2. test for all browser (xp,linux..)
    pool = pooler.get_pool(cr.dbname)
    tran_obj = pool.get('ir.translation')
    in_lang = 'en'
    ids = data['ids']
    translation_data = tran_obj.browse(cr, uid, ids, context)

    for trans in translation_data:
        if trans.need_review:
            continue
        if 'lang' in context and context['lang']:
            in_lang = context['lang'][:2].lower().encode('utf-8')

        if not trans['lang'] or not trans['src']:
            raise osv.except_osv('Warning !',
                                     'Please provide language and source')
        out_lang = trans['lang'][:2].lower().encode('utf-8')
        src = trans['src'].encode('utf-8')
        setUserAgent("Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008070400 SUSE/3.0.1-0.1 Firefox/3.0.1")

        try:
            post_params = urllib.urlencode({"langpair":"%s|%s" %(in_lang, out_lang), "text":src,"ie":"UTF8", "oe":"UTF8"})
        except KeyError, error:
            return

        page = urllib.urlopen("http://translate.google.com/translate_t", post_params)
        content = page.read()
        page.close()
        match = re.search("<div id=result_box dir=\"ltr\">(.*?)</div>", content)
        value = src
        if match:
            value = match.groups()[0]
        tran_obj.write(cr, uid, trans.id, {'value':value, 'need_review':True})
    return {}

class google_translate_wizard(wizard.interface):
    states = {
        'init': {
             'actions': [],
                'result': {'type': 'form', 'arch':trans_form, 'fields':trans_fields, 'state':[('end','Cancel','gtk-cancel'),('translate','Translate','gtk-ok')]}
                },
        'translate': {
                'actions': [_translate],
                'result': {'type': 'form', 'arch':trans_sum, 'fields':trans_sum_fields, 'state':[('end','OK','gtk-ok')]}
                },
            }

google_translate_wizard('google.translate.wizard')
