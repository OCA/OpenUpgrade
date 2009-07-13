# -*- encoding: utf-8 -*-
##############################################################################
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
import time


class invoice_create(wizard.interface):
    """Create an invoice based on selected timesheet lines"""
    def _get_accounts(self, cr, uid, data, context):
        """give the default aa that are recursively linked to timesheet line
        it will retviev the upper level parent account"""
        if not len(data['ids']):
            return {}
        ids = ','.join(map(str,data['ids']))
        try :
            cr.execute   (
                            "SELECT distinct(a.parent_id) \
                            from account_analytic_account \
                            a join account_analytic_line l \
                            on (l.account_id=a.id) where l.id IN (%s) ;" %(ids,)
                            )
            projects_ids = cr.fetchall()
            cr.execute(
                        "SELECT l.id from account_analytic_account \
                         a join account_analytic_line l \
                         on (l.account_id=a.id) \
                         where l.id IN (%s) \
                         and invoice_id is not null;"%(ids,)
                    )
            test=cr.fetchall()
            if len (test)>0:
                raise wizard.except_wizard(
                                            'Error !', 
                                            'Please select only line wich \
                                             are not already invoiced !!!'
                                            )
        except Exception, e :
            cr.rollback()
            raise wizard.except_wizard(
                                        'Error !', 
                                         str(e)
                                      )
        
        # on retourne les parents dinstinct
        return {'projects': [x[0] for x in projects_ids]}

     def _do_create(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        projects_ids = data['form']['projects'][0][2]
        invoices = []
        for project in pool.get('account.analytic.account').browse(
                                                                    cr, 
                                                                    uid, 
                                                                    projects_ids, 
                                                                    context
                                                                ):
            ## We retrived the invoice data for the
            ## AA we want to invoice
            partner = project.partner_id
            if (not partner) or not (project.pricelist_id):
                raise wizard.except_wizard(
                            'Analytic account incomplete', 
                            'Please fill in the pricelist and the partner field in the analytic\
                             account:%s \
                             \n The parent account must always be complete.\
                             ' % (project.name)
                            )
            ## We retriev the invoicing contact
            if project.contact_id:
                inv_contact = project.contact_id.id
            else:
                inv_contact = pool.get('res.partner').address_get(
                                                        cr, 
                                                        uid, 
                                                        [project.partner_id.id], 
                                                        adr_pref=['invoice']
                                                    )['invoice']
            date_invoice = time.strftime('%Y-%m-%d')
            date_due=False
            # Compute date_due
            if partner.property_payment_term.id:
                pt_obj = pool.get('account.payment.term')
                if not date_invoice :
                    date_invoice= time.strftime('%Y-%m-%d')
                pterm_list = pt_obj.compute(
                                                cr, 
                                                uid, 
                                                partner.property_payment_term.id, 
                                                value=1, 
                                                date_ref=date_invoice
                                            )
                if pterm_list:
                    pterm_list = [line[0] for line in pterm_list]
                    pterm_list.sort()
                date_due=pterm_list[-1]
                
            # we retriev the parent account for generating invoice name 
            # If no parent, take this level
            project_name = project.name
            if project.parent_id:
                parent_project = pool.get('account.analytic.account').browse(
                                                                cr, 
                                                                uid, 
                                                                [project.parent_id.id], 
                                                                context
                                                            )[0]
                project_name = parent_project.name
            
            # Attention au type de facture !
            address_contact_id = pool.get('res.partner').address_get(
                                                            cr, 
                                                            uid, 
                                                            [project.partner_id.id], 
                                                            adr_pref=['contact']
                                                        )
            curr_invoice = {
                'name': time.strftime('%D')+' - '+project_name,
                'partner_id': project.partner_id.id,
                'address_contact_id': address_contact_id['contact'],
                'address_invoice_id': inv_contact,
                'payment_term': partner.property_payment_term.id or False,
                'account_id': partner.property_account_receivable.id,
                'currency_id': project.pricelist_id.currency_id.id,
                'date_due': date_due,
                'date_invoice':date_invoice,
                
            }
            
            last_invoice = pool.get('account.invoice').create(
                                                                cr, 
                                                                uid, 
                                                                curr_invoice
                                                            )
            invoices.append(last_invoice)
            context2 = context.copy()
            context2['lang'] = partner.lang
            # For each childs account
            for account in project.child_ids:
                try :
                    cr.execute(
                                "SELECT line.product_id,line.to_invoice,\
                                sum(line.unit_amount),line.journal_id,\
                                sum(line.amount) \
                                FROM account_analytic_line as line \
                                join account_analytic_journal journal \
                                on (journal.id=line.journal_id) \
                                WHERE line.account_id = %s \
                                and line.id IN (%s) \
                                GROUP BY line.product_id,line.to_invoice,\
                                line.journal_id"%(
                                                account.id,
                                                ','.join(map(str,data['ids']))
                                                )
                            )
                    acc_line_to_invoice=cr.fetchall()
                except Exception, e :
                    cr.rollback()
                    raise wizard.except_wizard(
                                        'Error !', 
                                         str(e)
                                      )
                
                for product_id,factor_id,qty,journal,amount in acc_line_to_invoice:
                    if not factor_id:
                        raise wizard.except_wizard(
                                            'Error !', 
                                            'Each of the selected lines must \
                                            have invoice factor!!!'
                                        )
                    if not factor_id :
                        factor_id = project.factor_id.id
                    product = pool.get('product.product').browse(
                                                                    cr, 
                                                                    uid, 
                                                                    product_id, 
                                                                    context2
                                                                )
                    if not product:
                        raise wizard.except_wizard(
                                                    'Error', 
                                                    'At least on line \
                                                     have no product !'
                                                    )
                    factor_name = ''
                    factor = pool.get('hr_timesheet_invoice.factor').browse(
                                                                        cr, 
                                                                        uid, 
                                                                        factor_id, 
                                                                        context2
                                                                    )
                    if factor.customer_name:
                        factor_name = product.name+' - '+factor.customer_name
                    else:
                        factor_name = product.name
                    
                    journal_obj=pool.get('account.analytic.journal').browse(
                                                                        cr, 
                                                                        uid, 
                                                                        journal, 
                                                                        context2
                                                                    )
                    
                    if journal_obj.type == 'purchase':
                        # Reste a convertir dans la monnaie du projet
                        currency_obj = pool.get('res.currency')
                        line_currency_obj = currency_obj.browse(
                                                cr,
                                                uid,
                                                [project.pricelist_id.currency_id.id]
                                            )[0]
                        
                        company = pool.get('res.users').browse(cr,uid,uid).company_id
                        
                        company_currency = currency_obj.browse(
                                                                cr,
                                                                uid,
                                                                [company.currency_id.id]
                                                            )[0]
                        price_tmp = currency_obj.compute(
                                                         cr, 
                                                         uid, 
                                                         company_currency.id, 
                                                         line_currency_obj.id, 
                                                         abs(amount),
                                                         context
                                                        )
                        price = price_tmp/(qty or 1.0)
                    else:
                        price = 0.0
                        pl = project.pricelist_id.id
                        price = pool.get('product.pricelist').price_get(
                                                            cr,
                                                            uid,
                                                            [pl], 
                                                            product_id, 
                                                            qty or 1.0, 
                                                            project.partner_id.id
                                                        )[pl]
                    taxes = product.taxes_id
                    # if account.partner_id.property_account_tax:
                    #                         taxep = account.partner_id.property_account_tax
                    #                     else:
                    #                         taxep = project.partner_id.property_account_tax
                    # if not taxep:
                    tax = [x.id for x in taxes or []]
                    # else:
                    #                         tax = [taxep[0]]
                    #                         tp = pool.get('account.tax').browse(cr, uid, taxep[0])
                    #                         for t in taxes:
                    #                             if not t.tax_group==tp.tax_group:
                    #                                 tax.append(t.id)
                    
                    account_id = product.product_tmpl_id.property_account_income\
                        or product.categ_id.property_account_income_categ
                
                    curr_line = {
                        'price_unit': price,
                        'quantity': qty,
                        'discount':factor.factor,
                        'invoice_line_tax_id': [(6,0,tax )],
                        'invoice_id': last_invoice,
                        'name': factor_name,
                        'product_id': data['form']['product'] or product_id,
                        'invoice_line_tax_id': [(6,0,tax)],
                        'uos_id': product.uom_id.id,
                        'account_id': account_id.id,
                        'account_analytic_id': account.id,
                    }

                    #
                    # Compute for lines
                    #
                    try :
                        cr.execute(
                                    "SELECT * FROM account_analytic_line \
                                    WHERE account_id = %s \
                                    and id IN (%s) \
                                    AND product_id=%s \
                                    and to_invoice=%s"%(
                                        account.id, ','.join(map(str,data['ids'])), 
                                        product_id, factor_id
                                    )
                                )
                        line_ids = cr.dictfetchall()
                    except Exception, e :
                        cr.rollback()
                        raise wizard.except_wizard(
                                                    'Error !', 
                                                     str(e)
                                                    )
                    note = []
                    for line in line_ids:
                        # set invoice_line_note
                        details = []
                        if data['form']['date']:
                            details.append(line['date'])
                        p_uom = pool.get('product.uom').browse(
                                                            cr, 
                                                            uid, 
                                                            [line['product_uom_id']]
                                                            )[0].name
                        if data['form']['time']:
                            details.append(
                                            "%s %s" % (
                                                        line['unit_amount'], 
                                                        p_uom,
                                                        )
                                            )

                        if data['form']['name']:
                            details.append(line['name'])
                        
                        note.append(' - '.join(details))

                    curr_line['note'] = "\n".join(note)
                    pool.get('account.invoice.line').create(cr, uid, curr_line)
                    try :
                        cr.execute(
                                        "update account_analytic_line \
                                        set invoice_id=%s \
                                        WHERE account_id = %s \
                                        and id IN (%s)"%
                                        (
                                            last_invoice,account.id, 
                                            ','.join(map(str,data['ids']))
                                        )
                                    )
                    except Exception, e :
                        cr.rollback()
                        raise wizard.except_wizard(
                                                    'Error !', 
                                                     str(e)
                                                    )
                        
        cr.execute("\
                    select id from ir_ui_view \
                    where model='account.invoice' \
                    and name = 'account.invoice.form';"
                ),
        ids = cr.fetchall()
        return {
            'domain': "[('id','in', ["+','.join(map(str,invoices))+"])]",
            'name': 'Invoices',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'view_id': ids[0],
            'context': "{'type':'out_invoice'}",
            'type': 'ir.actions.act_window',
            'res_id':invoices
        }


    _create_form = """<?xml version="1.0"?>
    <form string="Invoice on analytic entries">
        <separator string="Do you want details for 
each line of the invoices ?" colspan="4"/>
        <field name="date"/>
        <field name="time"/>
        <field name="name"/>
        <field name="price"/>
        <separator string="Choose projects you want to invoice" colspan="4"/>
        <field name="projects" colspan="4">
                
        </field>
        <separator string="Choose a product for intermediary invoice" 
        colspan="4"/>
        <field name="product"/>
    </form>"""
    _create_fields = {
        'projects': {
                        'string':'Projects', 
                        'type':'many2many', 
                        'required':'true', 
                        'relation':'account.analytic.account',
                        'help' :  '(watch out the proposed acccount are \n \
                                    the upper level parent account \n \
                                    if you want to invoice them directely \n \
                                    select the last level account)'
                    },
        'date': {
                    'string':'Date', 
                    'type':'boolean'
                },
        'time': {
                    'string':'Time spent', 
                    'type':'boolean'
                },
        'name': {
                    'string':'Name of entry', 
                    'type':'boolean'
                },
        'price': {
                    'string':'Cost', 
                    'type':'boolean'
                },
        'product': {
                    'string':'Product', 
                    'type':'many2one', 
                    'relation': 'product.product'
                },
    }

    states = {
        'init' : {
            'actions' : [_get_accounts], 
            'result' : {
                            'type':'form', 
                            'arch':_create_form, 
                            'fields':_create_fields, 
                            'state': [
                                        ('end','Cancel'),
                                        ('create','Create invoices')
                                    ]
                        },
        },
        'create' : {
            'actions' : [],
            'result' : {
                            'type':'action', 
                            'action':_do_create, 
                            'state':'end'
                        },
        },
    }
invoice_create('invoice.create')
