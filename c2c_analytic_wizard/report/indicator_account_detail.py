# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) Camptocamp (http://www.camptocamp.com) All Rights Reserved.
#
# $Id$
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


from report.interface import report_int

from c2c_reporting_tools.translation import _
from c2c_reporting_tools.templates.standard_template import *
from c2c_reporting_tools.flowables.key_value_table import *
from c2c_reporting_tools.flowables.simple_row_table import *
from c2c_reporting_tools.c2c_helper import *
import pooler
import netsvc
import time


class indicator_account_detail(report_int): 
    """ report """

    logger = None
    
    downpayments_ids = []
    
    def __init__(self, name):
        """ constructor """
        self.logger = netsvc.Logger()
        super(indicator_account_detail, self).__init__(name)
        
        
        
        
    def _get_detail_builder(self, cr, context, project):
        """ return the table that contain project details """
        
        builder = KeyValueTableBuilder(_("Details"))
        
        #simple table one column of keys, one column of values
        builder.add_key_column(30*mm)
        builder.add_value_column()
        
        ###
        # add pairs of key & value
        ###
        
        builder.add_key_cell(_("Name:"))
        builder.add_text_cell( project.name )

        builder.add_key_cell(_("Code:"))
        builder.add_text_cell( project.code )
        
        builder.add_key_cell(_("Parent Project:"))
        builder.add_text_cell(
                            (project.parent_id and project.parent_id.code or '')+\
                            " "+\
                            (project.parent_id and project.parent_id.name or '-')
                        )
        
        builder.add_key_cell(_("Customer:"))
        builder.add_text_cell(
                        project.partner_id and \
                        project.partner_id.name or '-'
                    )

        builder.add_key_cell(_("Contact:"))
        builder.add_text_cell(
                                project.contact_id and\
                                project.contact_id.name or '-'
                            )

        builder.add_key_cell(_("Manager:"))
        builder.add_text_cell(
                                project.user_id and\
                                 project.user_id.name or '-'
                            )
               
        return builder
        
        
        
        
    def _get_indicator_builder(self, cr, context, project):
        """ return the table that contain indicators """

        
        builder = KeyValueTableBuilder(_("Indicators"))
        builder.add_key_column()
        builder.add_value_column()
        builder.add_key_column()
        builder.add_value_column()
        
        builder.add_key_cell(_("Theorical Revenue:"))
        amount = self.accounts._ca_theorical_calc(
                                            self.cr, 
                                            self.uid, 
                                            [project.id], 
                                            "", 
                                            {}
                                        )[project.id]
        currency = project.company_id.currency_id.name
        builder.add_money_cell(amount, currency)
        
        builder.add_key_cell(_("Hours Tot:"))
        hours = self.accounts._hours_quantity_calc(
                                                    self.cr, 
                                                    self.uid, 
                                                    [project.id], 
                                                    "", 
                                                    {}
                                                )[project.id]
        builder.add_num_cell(hours)
        
        builder.add_key_cell(_("Invoiced Amount:"))
        amount = self.accounts._ca_invoiced_calc(
                                                    self.cr, 
                                                    self.uid, 
                                                    [project.id], 
                                                    "", 
                                                    {}
                                            )[project.id]
        currency = project.company_id.currency_id.name
        builder.add_money_cell(
                                amount, 
                                currency
                            )      
        
        builder.add_key_cell(_("Invoiced Hours:"))
        hours = self.accounts._hours_qtt_invoiced_calc(
                                                        self.cr, 
                                                        self.uid, 
                                                        [project.id], 
                                                        "", 
                                                        {}
                                                )[project.id]
        builder.add_num_cell(hours)
        
        builder.add_key_cell(_("Remaining Revenue:"))
        amount = self.accounts._remaining_ca_calc(
                                                    self.cr, 
                                                    self.uid, 
                                                    [project.id], 
                                                    "", 
                                                    {}
                                                )[project.id]
        currency = project.company_id.currency_id.name
        builder.add_money_cell(amount, currency)
        
        builder.add_key_cell(_("Remaining Hours:"))
        hours = self.accounts._remaining_hours_calc(
                                                    self.cr, 
                                                    self.uid, 
                                                    [project.id], 
                                                    "", 
                                                    {}
                                                )[project.id]
        builder.add_num_cell(hours)
        
        builder.add_key_cell(_("Uninvoiced Amount:"))
        amount = self.accounts._ca_to_invoice_calc(
                                                    self.cr, 
                                                    self.uid, 
                                                    [project.id], 
                                                    "", 
                                                    {}
                                                )[project.id]
        currency = project.company_id.currency_id.name
        builder.add_money_cell(amount, currency)
        
        builder.add_key_cell(_("Uninvoiced Hours:"))
        hours = self.accounts._hours_qtt_non_invoiced_calc(
                                                            self.cr, 
                                                            self.uid, 
                                                            [project.id], 
                                                            "", 
                                                            {}
                                                    )[project.id]
        builder.add_num_cell(hours)
        
        builder.add_key_cell(_('Max Invoice Price:'))
        amount = project.amount_max
        currency = project.company_id.currency_id.name
        builder.add_money_cell(amount, currency)
        
        builder.add_key_cell(_('Maximal Hours:'))
        amount = project.quantity_max
        builder.add_num_cell(amount)
        
        
        builder.add_key_cell(_("Last Invoice Date:"))
        date = self.accounts._last_invoice_date_calc(
                                                        self.cr, 
                                                        self.uid, 
                                                        [project.id], 
                                                        "", 
                                                        {}
                                                )[project.id]
        if date == "":
            date = None
        builder.add_date_cell(date)
        
        builder.add_key_cell(_("Last Invoiced Worked Date:"))
        date = self.accounts._last_worked_invoiced_date_calc(
                                                            self.cr, 
                                                            self.uid,
                                                            [project.id], 
                                                            "", 
                                                            {}
                                                        )[project.id]
        if date == "":
            date = None
        builder.add_date_cell(date)
        
        builder.add_key_cell(_("Last Worked Date:"))
        date = self.accounts._last_worked_date_calc(
                                                    self.cr, 
                                                    self.uid, 
                                                    [project.id], 
                                                    "", 
                                                    {}
                                            )[project.id]
        if date == "":
            date = None
        builder.add_date_cell(date)

        return builder



    def get_taxes_amount(self, taxes, amount, address, product, partner):
        """ return the resulting value of the taxes applied on the amount """
        tax_total = 0
        for tax in taxes:

            #compute the tax
            if tax.type == 'percent': 
                tax_value = amount * tax.amount
            elif tax.type == 'fixed':
                tax_value = tax.amount
            elif tax.type == 'code':
                localdict = {
                                'price_unit':amount, 
                                'address': address, 
                                'product':product, 
                                'partner': partner
                            }
                exec tax.python_compute in localdict
                tax_value = localdict.get('result', 0)
            else:  #tax.type == 'none'  
                tax_value = 0


            #if the tax has children we must take them in account
            if len(tax.child_ids) > 0:
                #only children tax computation results are taken in account
                if tax.child_depend:
                    sub_tax_value = 0
                    tax_value = self.get_taxes_amount(
                                                        tax.child_ids, 
                                                        tax_value, 
                                                        address, 
                                                        product, 
                                                        partner
                                                    )
                #children tax computation results are taken in account in addition to parent tax 
                else:
                    tax_value += self.get_taxes_amount(
                                                        tax.child_ids, 
                                                        tax_value, 
                                                        address, 
                                                        product, 
                                                        partner
                                                    )

            tax_total += tax_value
        return tax_total
        
        
    def get_down_payments(self, account):
        """return the list of payments linked to a given product (the product is defined hardcorded as a object's var)"""
        
        lines = []
        
        return_values = []
                
        res_lines = self.pool.get('account.invoice.line')
        
        
        #if we must search through all the children too
        project_children = [account.id]
        #go recursivly down the child tree to collect all children ids
        children =  account.child_ids;
        
        while len(children) > 0:
            #store the children ids in the main list
            for child in children:
                project_children.append(child.id);
            parents = children
            children = []
            
            #go deeper
            for parent in parents:
                for child in parent.child_ids:
                    children.append(child)        
        
        
        # get line ids
        # (I replaced here the %&@!! ORM search function by this query because of the "order by" clause on another table)
        query = """ SELECT lin.id 
                    FROM account_invoice_line lin, account_invoice inv
                    WHERE lin.invoice_id = inv.id
                    AND lin.product_id in (%s )
                    AND lin.account_analytic_id in (%s)
                    ORDER BY inv.date_invoice DESC 
                """ % (",".join(map(str,self.downpayments_ids)), ",".join(map(str,project_children)))
        print query
        try :
            self.cr.execute(query)
        except Exception, e:
            self.cr.rollback()
            raise str(e)

        line_ids = map(lambda x:x[0], self.cr.fetchall())
        if (len(line_ids) > 0):
            lines = res_lines.browse(self.cr, self.uid, line_ids, {})
            
            
        for line in lines:

           
            
            line_values = {}
            line_values['date'] = line.invoice_id.date_invoice
            line_values['name'] = line.name
            line_values['nbr'] = line.invoice_id.number

            if line.invoice_id.price_type == 'tax_excluded':
                tax_value = self.get_taxes_amount(line.invoice_line_tax_id, line.price_subtotal, line.invoice_id.address_invoice_id, line.product_id, line.invoice_id.partner_id)
            else: #line.price_type == 'tax_included'
                tax_value = 0
            line_values['amount'] = line.price_subtotal + tax_value
            
            price_in_company_currency = c2c_helper.exchange_currency(self.cr, line_values['amount'], line.invoice_id.currency_id.id, account.company_id.currency_id.id, time.strptime(line.invoice_id.date_invoice, "%Y-%m-%d"))
            line_values['amount_company_currency'] = price_in_company_currency
            
            line_values['currency'] = line.invoice_id.currency_id.name
            return_values.append(line_values)
            #self.add_down_payments_sum(account, line.price_unit, price_in_company_currency)
            
        return return_values
        
        
        
    def _get_downpayement_builder(self, cr, context, project):
        """ return the downpayment table """
        
        builder = SimpleRowsTableBuilder(_("Down Payments"))
        builder.add_date_column(_("Date"), 20*mm)
        builder.add_text_column(_("Description"))
        builder.add_text_column(_("Invoice"))
        builder.add_money_column(_("Amount"))
        builder.add_money_column(_("Amount")+" ["+project.company_id.currency_id.name+"]")
        
        payments = self.get_down_payments(project)
        
        if len(payments) == 0:
            return False
        
        for p in payments: 
            builder.add_date_cell(time.strptime(p['date'], "%Y-%m-%d"))
            builder.add_text_cell(p['name'])
            builder.add_text_cell(p['nbr'])
            builder.add_money_cell(p['amount'], p['currency'])
            builder.add_money_cell(p['amount_company_currency'], project.company_id.currency_id.name)
        
        builder.add_empty_cell()
        builder.add_text_cell("<b>Total:</b>")
        builder.add_empty_cell()
        builder.add_empty_cell()
        builder.add_subtotal_money_cell(project.company_id.currency_id.name)
                
        return builder


    def get_invoices(self, account, open_only, supplier):
        """ return the invoices of a project  (IHMJ) """
        
        #if we must search through all the children too
        project_children = [account.id]
        #go recursivly down the child tree to collect all children ids
        children =  account.child_ids;
        
        while len(children) > 0:
            #store the children ids in the main list
            for child in children:
                project_children.append(child.id);
            parents = children
            children = []
            
            #go deeper
            for parent in parents:
                for child in parent.child_ids:
                    children.append(child)        
        
        #depending on the user choices, we build the query
        if open_only:
            open_only_sql=" AND (inv.state = 'open' or inv.state = 'sent')"
        else:
            open_only_sql=''
            
        # supplier invoices
        if supplier:
            supplier_sql=" AND inv.type= 'in_invoice'"
        # customer invoices
        else: 
            supplier_sql=" AND inv.type= 'out_invoice'"
        
        project_children_sql = ",".join(map(str,project_children))       
        
       # get the invoices lines that are releated to the project
        query = ''' 
            SELECT lin.id 
            FROM account_invoice inv, account_invoice_line lin
            WHERE lin.account_analytic_id IN (%s)
              AND inv.id = lin.invoice_id
              %s
              %s            
            ORDER BY date_due DESC 
        ''' % (project_children_sql, open_only_sql, supplier_sql)
        self.cr.execute(query)
        lines_ids = map(lambda x:x['id'],self.cr.dictfetchall())
        
        lines = []
        if lines_ids:
            lines =  self.pool.get('account.invoice.line').browse(self.cr,self.uid,lines_ids, {})
        
        invoices = {}
        invoices_order = []
        
        #for each line, find the amount and taxes
        for l in lines:
            #init the array if the invoice does not exists in it: 
            if l.invoice_id.id not in invoices:
                invoices[l.invoice_id.id] = {}
                invoices[l.invoice_id.id]['object'] = l.invoice_id
                invoices[l.invoice_id.id]['total'] = 0
                invoices[l.invoice_id.id]['total_currency'] = 0
                #keep the invoices ordered
                invoices_order.append(l.invoice_id.id)

            # get the line taxes 
            if l.invoice_id.price_type == 'tax_excluded':
                tax_value = self.get_taxes_amount(l.invoice_line_tax_id, l.price_subtotal, l.invoice_id.address_invoice_id, l.product_id, l.invoice_id.partner_id)
            else: #line.price_type == 'tax_included'
                tax_value = 0
                     
            line_total = l.price_subtotal + tax_value
            invoices[l.invoice_id.id]['total'] += line_total
            invoices[l.invoice_id.id]['total_currency'] += c2c_helper.exchange_currency(self.cr, line_total, l.invoice_id.currency_id.id, account.company_id.currency_id.id, time.strptime(l.invoice_id.date_invoice, "%Y-%m-%d"))
                        
            
        #reorder result
        ordered_invoices = []
        for id in invoices_order:
            ordered_invoices.append(invoices[id])
        return ordered_invoices
        
        
        


    def get_invoices_old(self, account, open_only, supplier):
        """ return the invoices of a project """
        
        
        #if we must search through all the children too
        project_children = [account.id]
        #go recursivly down the child tree to collect all children ids
        children =  account.child_ids;
        
        while len(children) > 0:
            #store the children ids in the main list
            for child in children:
                project_children.append(child.id);
            parents = children
            children = []
            
            #go deeper
            for parent in parents:
                for child in parent.child_ids:
                    children.append(child)

        
        #depending on the user choices, we build the query
        if open_only:
            open_only_sql=" AND (inv.state = 'open' or inv.state = 'sent')"
        else:
            open_only_sql=''
            
        # supplier invoices
        if supplier:
            supplier_sql=" AND inv.type= 'in_invoice'"
        # customer invoices
        else: 
            supplier_sql=" AND inv.type= 'out_invoice'"
        
        project_children_sql = ",".join(map(str,project_children))       
        
        # get the invoices that are releated to the project
        query = ''' 
            SELECT inv.number as inv_number, inv.name, inv.date_due, 
            inv.amount_total, cur.name as currency, inv.state,
            par.name as partner_name
            FROM account_invoice inv, account_invoice_line lin, 
            res_currency cur, res_partner par
            WHERE lin.account_analytic_id IN (%s)
              AND inv.id = lin.invoice_id
              AND inv.currency_id = cur.id
              AND inv.partner_id = par.id
              %s
              %s            
            ORDER BY date_due DESC 
        ''' % (project_children_sql, open_only_sql, supplier_sql)
        self.cr.execute(query)
        try :
            invoices = self.cr.dictfetchall()
        except Exception, e:
            self.cr.rollback()
            raise str(e) 
        return invoices


        
        
    def _get_customer_invoice_builder(self, cr, context, project, open_only):
        """ Return the customer invoices flowable object
            Return false if there is no invoices        
        """
        builder = SimpleRowsTableBuilder(_("Customers Invoices"))
        builder.add_text_column(_("Ref"), 20*mm)
        builder.add_text_column(_("Description"))
        builder.add_text_column(_("State"), 15*mm)
        builder.add_date_column(_("Due Date"), 20*mm)
        builder.add_money_column(_("Amount"), 40*mm)
        builder.add_money_column(_("Amount")+" ["+project.company_id.currency_id.name+"]", 40*mm)
        
        invoices = self.get_invoices(project, open_only, False)
        if (len(invoices) == 0):
            return False
        
        for invoice in invoices:
            i = invoice['object']
            
            builder.add_text_cell(i.number)
            builder.add_text_cell(i.name)
            builder.add_text_cell(i.state)
            builder.add_date_cell(i.date_due)
            builder.add_money_cell(invoice['total'], i.currency_id.name)
            builder.add_money_cell(invoice['total_currency'], project.company_id.currency_id.name)

        
        builder.add_empty_cell()
        builder.add_text_cell("<b>Total:</b>")
        builder.add_empty_cell()
        builder.add_empty_cell()
        builder.add_empty_cell()
        builder.add_subtotal_money_cell(project.company_id.currency_id.name)
        
        
        return builder


    def _get_supplier_invoice_builder(self, cr, context, project, open_only):
        """ Return the supplier invoices flowable object. 
            Return false if there is no invoices
        """
        builder = SimpleRowsTableBuilder(_("Suppliers Invoices"))
        builder.add_text_column(_("Ref"), 20*mm)
        builder.add_text_column(_("Description"))
        builder.add_text_column(_("Partner"))
        builder.add_text_column(_("State"), 15*mm)
        builder.add_date_column(_("Due Date"), 20*mm)
        builder.add_money_column(_("Amount"), 40*mm)
        builder.add_money_column(_("Amount")+" ["+project.company_id.currency_id.name+"]", 40*mm)
        
        invoices = self.get_invoices(project, open_only, True)
        if (len(invoices) == 0):
            return False
        
        for invoice in invoices:
            total = invoice['total']
            i = invoice['object']
            builder.add_text_cell(i.number)
            builder.add_text_cell(i.name)
            builder.add_text_cell(i.partner_id.name)
            builder.add_text_cell(i.state)
            builder.add_date_cell(i.date_due)
            builder.add_money_cell(total, i.currency_id.name)
            builder.add_money_cell(invoice['total_currency'], project.company_id.currency_id.name)
        

        builder.add_empty_cell()
        builder.add_text_cell("<b>Total:</b>")
        builder.add_empty_cell()
        builder.add_empty_cell()
        builder.add_empty_cell()
        builder.add_empty_cell()
        builder.add_subtotal_money_cell(project.company_id.currency_id.name)
        
        
        return builder



    def create(self, cr, uid, ids, datas, context={}):
        """ construct the report """

        #init
        self.cr = cr
        self.uid= uid
        self.datas = datas
        self.context = context              
        self.pool = pooler.get_pool(self.cr.dbname)
        
        #get the is of products flagged as downpayment
        self.downpayments_ids =  self.pool.get('product.product').search(self.cr, self.uid, [('downpayment', '=', 'true')])
        if not self.downpayments_ids :
            raise wizard.except_wizard(
                                        'Error !', 
                                         'No down product defined'
                                      )


        self.accounts = self.pool.get('account.analytic.account')
                    
        #retrive info from the wizard
        open_only = False
        if 'form' in self.datas and 'open_only' in self.datas['form']:
                open_only = self.datas['form']['open_only']
                
        supplier_too = False
        if 'form' in self.datas and 'supplier_too' in self.datas['form']:
                supplier_too = self.datas['form']['supplier_too']

        #template
        doc = STPortraitTotalPage()
        doc.report_name = _("Indicator Report")
        
        #company name
        user = self.pool.get('res.users').browse(cr,uid,uid, context)        
        doc.company_name = user.company_id.name
        

        story = []
        
        #for each projects
        projects = self.accounts.browse(self.cr, self.uid, ids)
        for p in projects: 

        
            #detail block
            builder = self._get_detail_builder(cr, context, p)
            story.append(builder.get_table())

            
            #indicator block
            builder = self._get_indicator_builder(cr, context, p)
            story.append(Spacer(0, 8*mm))
            story.append(builder.get_table())

            
            #downpayement block
            builder = self._get_downpayement_builder(cr, context, p)
            if builder != False:
                story.append(Spacer(0, 8*mm))
                story.append(builder.get_table())

            
            #customer invoice
            builder = self._get_customer_invoice_builder(cr, context, p, open_only)
            #display the table only if there is lines in it
            if builder != False:
                story.append(Spacer(0, 8*mm))
                story.append(builder.get_table())

            
            #supplier invoice
            if supplier_too: 
                builder = self._get_supplier_invoice_builder(cr, context, p, open_only)
                #display the table only if there is lines in it
                if builder != False:
                    story.append(Spacer(0, 8*mm))
                    story.append(builder.get_table())
            
            #start a new page for each projet
            story.append(PageBreak())
            
                        
        return doc.fillWith(story)


indicator_account_detail('report.indicator.account.detail')
