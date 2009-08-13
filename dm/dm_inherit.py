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

from osv import fields
from osv import osv

class res_country(osv.osv):#{{{
    _name = 'res.country'
    _inherit = 'res.country'
    _columns = {
        'main_language' : fields.many2one('res.lang','Main Language',ondelete='cascade',),
        'main_currency' : fields.many2one('res.currency','Main Currency',ondelete='cascade'),
        'forwarding_charge' : fields.float('Forwarding Charge', digits=(16,2)),
        'payment_method_ids' : fields.many2many('account.journal','country_payment_method_rel','country_id','journal_id','Payment Methods',domain=[('type','=','cash')]),
    }
res_country()#}}}

class res_partner(osv.osv):#{{{
    _name = "res.partner"
    _inherit="res.partner"
    _columns = {
        'country_ids' : fields.many2many('res.country', 'partner_country_rel', 'partner_id', 'country_id', 'Allowed Countries'),
        'state_ids' : fields.many2many('res.country.state','partner_state_rel', 'partner_id', 'state_id', 'Allowed States'),
        'deceased' : fields.boolean('Deceased'),
        'deceased_date' : fields.datetime('Deceased Date'),
        'language_ids' : fields.many2many('res.lang','dm_customer_langs','lang_id','customer_id','Other Languages'),
        'prospect_media_ids' : fields.many2many('dm.media','dm_customer_prospect_media','prospect_media_id','customer_id','Prospect for Media'),
        'client_media_ids' : fields.many2many('dm.media','dm_customer_client_media','client_media_id','customer_id','Client for Media'),
        'decoy_address' : fields.boolean('Decoy Address', help='A decoy address is an address used to identify unleagal uses of a customers file'),
        'decoy_owner' : fields.many2one('res.partner','Decoy Address Owner', help='The partner this decoy address belongs to'),
        'decoy_external_ref' : fields.char('External Reference', size=64, help='The reference of the decoy address for the owner'),
        'decoy_media_ids': fields.many2many('dm.media','dm_decoy_media_rel','decoy_media_id','customer_id','decoy address for Media'),
        'decoy_for_campaign': fields.boolean('Used for Campaigns', help='Define if this decoy address can be used with campaigns'),
        'decoy_for_renting': fields.boolean('Used for File Renting', help='Define if this decoy address can be used with used with customers files renting'),

    }
    def _default_category(self, cr, uid, context={}):
        if 'category_id' in context and context['category_id']:
            return [context['category_id']]
        elif 'category' in context and context['category']:
            id_cat = self.pool.get('res.partner.category').search(cr,uid,[('name','ilike',context['category'])])[0]
            return [id_cat]
        return []

    def _default_all_country(self, cr, uid, context={}):
        id_country = self.pool.get('res.country').search(cr,uid,[])
        return id_country

    def _default_all_state(self, cr, uid, context={}):
        id_state = self.pool.get('res.country.state').search(cr,uid,[])
        return id_state

    _defaults = {
        'category_id': _default_category,
        'country_ids': _default_all_country,
        'state_ids': _default_all_state,
    }
res_partner()#}}}

class purchase_order(osv.osv):#{{{
    _name = 'purchase.order'
    _inherit = 'purchase.order'
    _columns = {
        'dm_campaign_purchase_line' : fields.many2one('dm.campaign.purchase_line','DM Campaign Purchase Line'),
    }
purchase_order()#}}}

class project_task(osv.osv):#{{{
    _name = "project.task"
    _inherit = "project.task"
    context_data ={}

    def default_get(self, cr, uid, fields, context=None):
        if 'type' in context and 'project_id' in context:
            self.context_data = context.copy()
            self.context_data['flag'] = True
        else:
            self.context_data['flag'] = False
        return super(project_task, self).default_get(cr, uid, fields, context)

    def fields_view_get(self, cr, user, view_id=None, view_type='form', context=None, toolbar=False):
        result = super(project_task,self).fields_view_get(cr, user, view_id, view_type, context, toolbar)
        if 'flag' in self.context_data or 'type' in context:
            if 'project_id' in self.context_data:
                if result['type']=='form':
                    result['arch']= """<?xml version="1.0" encoding="utf-8"?>\n<form string="Task edition">\n<group colspan="6" col="6">\n<field name="name" select="1"/>\n<field name="project_id" readonly="1" select="1"/>\n
                        <field name="total_hours" widget="float_time"/>\n<field name="user_id" select="1"/>\n<field name="date_deadline" select="2"/>\n<field name="progress" widget="progressbar"/>\n</group>\n
                        <notebook colspan="4">\n<page string="Information">\n<field name="planned_hours" widget="float_time" on_change="onchange_planned(planned_hours,effective_hours)"/>\n<field name="delay_hours" widget="float_time"/>\n
                        <field name="remaining_hours" select="2" widget="float_time"/>\n<field name="effective_hours" widget="float_time"/>\n<field colspan="4" name="description" nolabel="1" select="2"/>\n
                        <field colspan="4" name="work_ids" nolabel="1"/>\n<newline/>\n<group col="11" colspan="4">\n<field name="state" select="1"/>\n<button name="do_draft" states="open" string="Set Draft" type="object"/>
                        <button name="do_open" states="pending,draft" string="Open" type="object"/>\n<button name="do_reopen" states="done,cancelled" string="Re-open" type="object"/>\n<button name="do_pending" states="open" string="Set Pending" type="object"/>\n
                        <button groups="base.group_extended" name="%(project.wizard_delegate_task)d" states="pending,open" string="Delegate" type="action"/>\n<button name="%(project.wizard_close_task)d" states="pending,open" string="Done" type="action"/>\n
                        <button name="do_cancel" states="draft,open,pending" string="Cancel" type="object"/>\n</group>\n</page>\n<page groups="base.group_extended" string="Delegations">\n
                        <field colspan="4" name="history" nolabel="1"/>\n<field colspan="4" height="150" name="child_ids" nolabel="1">\n<tree string="Delegated tasks">\n<field name="name"/>\n
                        <field name="user_id"/>\n<field name="date_deadline"/>\n<field name="planned_hours" widget="float_time"/>\n<field name="effective_hours" widget="float_time"/>\n<field name="state"/>\n</tree>\n
                        </field>\n<field colspan="4" name="parent_id"/>\n</page>\n<page groups="base.group_extended" string="Extra Info">\n<separator string="Planning" colspan="2"/>\n<separator string="Dates" colspan="2"/>\n<field name="priority"/>\n
                        <field name="date_start" select="2"/>\n<field name="sequence"/>\n<field name="date_close" select="2"/>\n<field name="type"/>\n<field name="active" select="2"/>\n
                        <field name="partner_id" select="2"/>\n<separator colspan="4" string="Notes"/>\n<field colspan="4" name="notes" nolabel="1"/>\n</page>\n</notebook>\n</form>"""
        return result
    
    def create(self,cr,uid,vals,context={}):
        if 'flag' in self.context_data:
            if 'type' in self.context_data:
                task_type = self.pool.get('project.task.type').search(cr,uid,[('name','=',self.context_data['type'])])[0]
                vals['type']=task_type
                vals['project_id']=self.context_data['project_id']
                self.context_data = {}
            if 'planned_hours' not in vals:
                vals['planned_hours'] = 0.0
        return super(project_task, self).create(cr, uid, vals, context)
    
    _columns = {
        'date_reviewed': fields.datetime('Reviewed Date'),
        'date_planned': fields.datetime('Planned Date'),
    }

project_task()#}}}

class sale_order(osv.osv):#{{{
    _name = "sale.order"
    _inherit="sale.order"
    _columns = {
        'offer_step_id': fields.many2one('dm.offer.step','Offer Step'),
        'segment_id' : fields.many2one('dm.campaign.proposition.segment','Segment'),
        'journal_id': fields.many2one('account.journal', 'Journal'),
        'lines_number' : fields.integer('Number of sale order lines'),
        'so_confirm_do' : fields.boolean('Auto confirm sale order'),
        'invoice_create_do' : fields.boolean('Auto create invoice'),
        'invoice_validate_do' : fields.boolean('Auto validate invoice'),
        'invoice_pay_do' : fields.boolean('Auto pay invoice'),
    }
    
sale_order()#}}}

class product_product(osv.osv): # {{{
    _name = "product.product"
    _inherit = "product.product"
    _columns = {
        'country_ids' : fields.many2many('res.country', 'product_country_rel', 'product_id', 'country_id', 'Allowed Countries'),
        'state_ids' : fields.many2many('res.country.state','product_state_rel', 'product_id', 'state_id', 'Allowed States'),
        'language_id' : fields.many2one('res.lang', 'Language'),
    }

    def _default_all_country(self, cr, uid, context={}):
        id_country = self.pool.get('res.country').search(cr,uid,[])
        return id_country

    def _default_all_state(self, cr, uid, context={}):
        id_state = self.pool.get('res.country.state').search(cr,uid,[])
        return id_state

    _defaults = {
        'country_ids': _default_all_country,
        'state_ids': _default_all_state,
    }

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context={}, count=False):
            result = super(product_product,self).search(cr,uid,args,offset,limit,order,context,count)
            if 'offer_id' in context and context['offer_id']:
                result = []
                offer_browse_id = self.pool.get('dm.offer').browse(cr,uid,context['offer_id'])
                for step in offer_browse_id.step_ids:
                    for item in step.item_ids:
                        result.append(item.id)
            return result
product_product() # }}}

class actions_server(osv.osv): # {{{
    _name = 'ir.actions.server'
    _inherit = 'ir.actions.server'
    _columns = {
        'dm_action' : fields.boolean('Action')
    }
actions_server() # }}}

#vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: