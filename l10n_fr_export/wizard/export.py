# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 SISTHEO - eric@everlibre.fr
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import wizard
import pooler
import base64
import time
import os
dates_form = '''<?xml version="1.0"?>
<form string="Select year">
    <field name="fiscalyear" colspan="4"/>
    <field name="directory" colspan="4" />
</form>'''

dates_fields = {
    'fiscalyear': {'string': 'Fiscal year', 'type': 'many2one', 'relation': 'account.fiscalyear', 'required': True},
    'directory': {'string': 'Directory ', 'type': 'char', 'size': 256, 'required': True,'help':'Storage Directory on server'}
}
def utf(val):
        if isinstance(val, str):
             str_utf8 = val
        elif isinstance(val, unicode):
             str_utf8 = val.encode('utf-8')
        else:
             str_utf8 = str(val)
        return str_utf8

class wizard_report(wizard.interface):
    def _get_defaults(self, cr, uid, data, context):
        fiscalyear_obj = pooler.get_pool(cr.dbname).get('account.fiscalyear')
        data['form']['fiscalyear'] =fiscalyear_obj.find(cr, uid)
        data['form']['directory']=os.getcwd()
        return data['form']

    def export(self,cr,uid,data,context):
        fy= pooler.get_pool(cr.dbname).get('account.fiscalyear').read(cr,uid,data['form']['fiscalyear'])
        period_ids = pooler.get_pool(cr.dbname).get('account.period').search(cr,uid,[('fiscalyear_id','=',data['form']['fiscalyear'])])
        move_line_ids = pooler.get_pool(cr.dbname).get('account.move.line').search(cr,uid,[('period_id','in',period_ids),('state','=','valid')])
        mvts=pooler.get_pool(cr.dbname).get('account.move.line').read(cr,uid,move_line_ids)
        value=u"Journal;date;N° de pièce;N° de compte;Libellé;Débit;Crédit;date Lettrage, Lettrage\r\n"
        datecreation= time.strftime('%Y-%m-%d-%H:%M:%S',time.localtime())
        namefile="Export "+fy['name']+datecreation+".csv"
        directory=data['form']['directory']
        if directory[-1] != os.sep :
            directory=directory+os.sep
        out_file=open(directory+namefile,"w")
        for mvt in mvts:
            value=value+mvt['journal_id'][1]+";"+ mvt['date']+";"+mvt['move_id'][1]+";"+mvt['account_id'][1]+";"+mvt['name']+";"+str(mvt['debit'])+";"+str(mvt['credit'])+";"
            if mvt['reconcile_id']:
                date_reconcile=pooler.get_pool(cr.dbname).get('account.move.reconcile').read(cr,uid,mvt['reconcile_id'][0])['create_date']
                value=value+str(date_reconcile)+";"+mvt['reconcile_id'][1]
            else:
                value=value+";"
            value=value+"\r\n"
            out_file.write(utf(value))
            value=""
        out_file.close()
        value=utf(value)
        attach={'name':namefile,
                'datas':base64.encodestring(value),
                'datas_fname':namefile,
                'res_model':'account.fiscalyear',
                'res_id':data['form']['fiscalyear']
                }
        res=pooler.get_pool(cr.dbname).get('ir.attachment').create(cr,uid,attach)
        return {}
    states = {
        'init': {
            'actions': [_get_defaults],
            'result': {'type':'form', 'arch':dates_form, 'fields':dates_fields, 'state':[('end','Cancel'),('export','Export')]}
        },
        'export': {
            'actions': [export],
            'result': {'type':'state',  'state':'end'}
        }
    }
wizard_report('l10n.fr.export.export')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

