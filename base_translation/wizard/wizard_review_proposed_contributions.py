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
import wizard
import tools
import csv
import pooler
import base_translation.translation


view_form_end = """<?xml version="1.0"?>
<form string="Language file loaded.">
    <image name="gtk-dialog-info" colspan="2"/>
    <group colspan="2" col="4">
        <separator string="Installation done" colspan="4"/>
        <label align="0.0" string="Csv file for the selected language has been successfully reviewed with the i18n file" colspan="4"/>
    </group>
    <label align="0.5" string="For more information about translation process ,you can consult : http://openerp.com/wiki/index.php/Translation_Process" colspan="4"/>
</form>"""

view_form = """<?xml version="1.0"?>
<form string="Language Selection">
    <image name="gtk-dialog-info" colspan="2"/>
    <group colspan="2" col="4">
    <separator string="Language List" colspan="4"/>
        <label align="0.0" string="Choose a language to install:" colspan="4"/>
        <field name="lang" colspan="4"/>
        <label align="0.0" string="Note that this operation may take a few minutes." colspan="4"/>
    </group>
    <label align="0.5" string="For more information about translation process ,you can consult : http://openerp.com/wiki/index.php/Translation_Process" colspan="4"/>
</form>"""

class wizard_review_proposed_contributions(wizard.interface):
    def _review_difference(self, cr, uid, data, context):
        lang = data['form']['lang']
        ir_translation = pooler.get_pool(cr.dbname).get('ir.translation')
        ir_translation_contrib = pooler.get_pool(cr.dbname).get('ir.translation.contribution')
        ids = ir_translation.search(cr,uid,[('lang','=',lang)])
        res = ir_translation.read(cr,uid,ids,['type','name','value','src'])
        new_res =map(lambda x:{'type':x['type'],'name':x['name'],'value':x['value'],'src':x['src']},res)
        filename = tools.config["root_path"] + "/i18n/" + lang + ".csv"
        reader = csv.DictReader(open(filename,'r'),delimiter=',')
        new_reader = map(lambda x:{'type':x['type'],'name':x['name'],'value':x['value'],'src':x['src'].replace('\n','')},reader)
        diff = filter(lambda x : x not in new_reader,new_res)
        fp = open("/home/tiny/Desktop/test.txt",'w').write(str(new_reader))
#        diff = filter(lambda x:x not in new_res,new_reader)    
        diff = []
        for l in new_res:
            if l in new_reader:
                continue
            diff.append(l)
        for d in diff:
            vals = {}
            ids = ir_translation.search(cr,uid,[('type','=',d['type']),('name','=',d['name']),('src','=',d['src']),('lang','=',lang)])
            res_id = ir_translation.read(cr,uid,ids,['res_id','lang'])[0]
            ids = ir_translation_contrib.search(cr,uid,[('type','=',d['type']),('name','=',d['name']),('src','=',d['src']),('lang','=',lang)])            
            if ids:
                ir_translation_contrib.write(cr,uid,ids,{'value':d['value'],'src':d['src']})
            if not ids:
                vals['type']=d['type']
                vals['name']=d['name']
                vals['src']=d['src']
                vals['value']=d['value']
                vals['res_id']=res_id['res_id']
                vals['lang'] = res_id['lang']
                vals['state']='draft'
                vals['upload']=False
                ir_translation_contrib.create(cr,uid,vals)
        return {}    
    def _get_language(sel, cr, uid,context):
        return base_translation.translation.get_language(cr,uid,context,model='ir_translation')
    
    fields_form = {
        'lang': {'string':'Language', 'type':'selection', 'selection':_get_language,'required':True
        },
    }    
    states = {
        'init': {
            'actions': [], 
            'result': {'type': 'form', 'arch': view_form, 'fields': fields_form,
                'state': [
                    ('end', 'Cancel', 'gtk-cancel'),
                    ('start', 'Review Difference', 'gtk-ok', True)
                ]
            }
        },
        'start': {
            'actions': [_review_difference],
            'result': {'type': 'form', 'arch': view_form_end, 'fields': {},
                'state': [
                    ('end', 'Ok', 'gtk-ok', True)
                ]
            }
        },
     }
wizard_review_proposed_contributions('review.proposed.contributions')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

