# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2009 SISTHEO
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

from mx import DateTime
import time

from osv import fields, osv
import pooler


class res_partner(osv.osv):
    _inherit = 'res.partner'
    def generate_account(self, cr, uid, ids, *args):
        property_obj = self.pool.get('ir.property')
        fields_obj = self.pool.get('ir.model.fields')
        config_id=self.pool.get('account.generation.config').search(cr,uid,[('name','=','default')])
        if not config_id:
            raise osv.except_osv(_('Error !'),_('You need to define an default account generation config'))
        else:
            config=self.pool.get('account.generation.config').read(cr,uid,config_id)[0]
        for id in ids:
            nbcar=config['nbcar']
            partner=self.pool.get('res.partner').read(cr, uid,[id])
            acct_customer='411'+partner[0]['name'][:nbcar]
            acct_supplier='401'+partner[0]['name'][:nbcar]
            query="select count(id) from account_account where substring(code,0,7)='"+acct_customer+"'"
            cr.execute(query)
            nbcpt=cr.fetchone()[0]
            inc=nbcpt+1
            code_customer=acct_customer+("0" * (3-len(str(inc))))+str(inc)
            query="select count(id) from account_account where substring(code,0,7)='"+acct_customer+"'"
            cr.execute(query)
            nbcpt=cr.fetchone()[0]
            inc=nbcpt+1
            code_supplier=acct_supplier+("0" * (3-len(str(inc))))+str(inc)
            parent_customer_id=config['customer'][0]
            parent_supplier_id=config['supplier'][0]
            if not  property_obj.search(cr, uid, [('name','=', 'property_account_receivable' ),('res_id','=','res.partner,'+str(id))]): 
                # cree client
                act = self.pool.get('account.account').read(cr,uid,[parent_customer_id])[0]
                account={}
                account['type']=u'receivable'
                account['name']=partner[0]['name']
                account['code']=code_customer
                account['company_id']=act['company_id'][0]
                account['parent_id']=parent_customer_id
                account['company_currency_id']=act['company_currency_id'][0]
                if act['currency_id']:
                    account['currency_id']=act['currency_id'][0]
                account['user_type']=act['user_type'][0]
                res=self.pool.get('account.account').create(cr,uid,account) 
                field = fields_obj.search(cr, uid, [('name','=','property_account_receivable'),('model','=','res.partner'),('relation','=','account.account')])
                properties={'company_id':account['company_id'],'name':'property_account_receivable','fields_id':field[0],'value':'account.account,'+str(res),'res_id':'res.partner,'+str(id)}
                property_obj.create(cr, uid, properties)
            
            if not  property_obj.search(cr, uid, [('name','=', 'property_account_payable' ),('res_id','=','res.partner,'+str(id))]): 
               # Cree fournissur
               act = self.pool.get('account.account').read(cr,uid,[parent_supplier_id])[0]
               account={}
               account['type']=u'payable'
               account['name']=partner[0]['name']
               account['code']=code_supplier
               account['company_id']=act['company_id'][0]
               account['parent_id']=parent_supplier_id
               account['company_currency_id']=act['company_currency_id'][0]
               if act['currency_id']:
                   account['currency_id']=act['currency_id'][0]
               account['user_type']=act['user_type'][0]
               res=self.pool.get('account.account').create(cr,uid,account)
               field = fields_obj.search(cr, uid, [('name','=','property_account_payable'),('model','=','res.partner'),('relation','=','account.account')])
               properties={'company_id':account['company_id'],'name':'property_account_payable','fields_id':field[0],'value':'account.account,'+str(res),'res_id':'res.partner,'+str(id)}
               property_obj.create(cr, uid, properties)
res_partner()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
