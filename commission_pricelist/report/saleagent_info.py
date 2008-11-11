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

import time
from report import report_sxw

class saleagent_info(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(saleagent_info, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'compute':self.compute,
            
        })
    
    
    def compute(self,sale_agent_id):
        result=[];
        res=[];
        sale_obj = self.pool.get('sale.agent').read(self.cr,self.uid,[sale_agent_id])[0];
        print "SALE_OBJECT",sale_obj;
        customes_ids = sale_obj['customer'];        
        print "Customer ids::",customes_ids
        ret_list = [];
        
        print "IN THE COMPUTE FUNCTION",customes_ids        
        append_list = []
        for cust_id in customes_ids:
            ret_dict = {}
            custmer_obj = self.pool.get('res.partner').browse(self.cr,self.uid,cust_id);
            ret_dict['name']= custmer_obj.name;
            pricelist_obj = self.pool.get('product.pricelist').browse(self.cr,self.uid,custmer_obj.property_product_pricelist[0]);
            ret_dict['commrate']= pricelist_obj.commrate;
            print "before append";
            ret_dict['invoices'] = self.partner_invoices(custmer_obj);
            print "\nafter append",ret_dict;
            ret_list.append(ret_dict);          
        #End for        
        
        print "Ret list of partner::",ret_list;
        return ret_list
#       return True


    def partner_invoices(self,partner_obj):
        ret_list = [];
        invoice_ids = self.pool.get('account.invoice').search(self.cr,self.uid,[('partner_id','=',partner_obj.id)]);
        print "Invoices ::",invoice_ids;
        
        for invoice_id in invoice_ids:
            ret_dict = {};
            invoice = self.pool.get('account.invoice').read(self.cr,self.uid,[invoice_id])[0];
            #print "Invoice ::",invoice;
            ret_dict['invoice_name'] = invoice['name'];
            ret_dict['date_invoice'] = invoice['date_invoice']
            ret_dict['number'] = invoice['number'];
            ret_dict['amount_total'] = invoice['amount_total'];
            ret_dict['state'] = invoice['state'];
            pricelist_obj = self.pool.get('product.pricelist').browse(self.cr,self.uid,partner_obj.property_product_pricelist[0]);
            
            ret_dict['comm'] = str(((int(invoice['amount_total']) * int(pricelist_obj.commrate))/100))                      
            ret_list.append(ret_dict);
        #end for invoice_id in invoice_ids:
        
        print "\n List in invoice::",ret_list;
        return ret_list;
    #end def partner_invoices(self,partner_obj):
report_sxw.report_sxw('report.saleagent.info', 'sale.agent', 'addons/saleagent/report/saleagent_info.rml', parser=saleagent_info)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

