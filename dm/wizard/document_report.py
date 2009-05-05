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
import pooler

class wizard_document_report(wizard.interface):

    report_list_form = '''<?xml version="1.0"?>
    <form string="Select Report">
        <field name="report" colspan="4"/>
        <field name="address_id" colspan="4"/>
    </form>'''
    def execute(self, db, uid, data, state='init', context=None):
        self.dm_wiz_data = data
        return super(wizard_document_report,self).execute(db, uid, data, state, context)
    
    def _print_report(self, cr, uid, data , context):
        report = pooler.get_pool(cr.dbname).get('ir.actions.report.xml').browse(cr, uid, data['form']['report'])
        self.states['print_report']['result']['report']=report.report_name
        return {}

    def _get_reports(self, cr, uid, context):
        document_id = self.dm_wiz_data['id']
        pool=pooler.get_pool(cr.dbname)
        group_obj=pool.get('ir.actions.report.xml')
        ids=group_obj.search(cr, uid, [('document_id','=',document_id)])
        res=[(group.id, group.name) for group in group_obj.browse(cr, uid, ids)]
        res.sort(lambda x,y: cmp(x[1],y[1]))
        return res    
    
    report_list_fields = {
                    
        'report': {'string': 'Select Report', 'type': 'selection', 'selection':_get_reports, },
        'address_id': {'string': 'Select Customer Address', 'type': 'many2one','relation':'res.partner.address', 'selection':_get_reports, 'domain':[('partner_id.category_id','=','DTP Preview Customers')] }
        
        }
    
    states = {
        'init': {
            'actions': [],
            'result': {'type':'form', 'arch':report_list_form, 'fields':report_list_fields, 'state':[('end','Cancel'),('print_report','Print Report'),]}
            },
        'print_report': {
            'actions': [_print_report],
            'result': {'type': 'print', 'report':'', 'state':'end'}
            },        
        }
wizard_document_report("wizard_document_report")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
