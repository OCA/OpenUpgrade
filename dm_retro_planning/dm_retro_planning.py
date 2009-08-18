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

class dm_campaign_group(osv.osv):#{{{
    _inherit = "dm.campaign.group"
    _columns = {
        'project_id' : fields.many2one('project.project', 'Project', readonly=True),
    }
dm_campaign_group()

class one2many_mod_task(fields.one2many):#{{{
    def get(self, cr, obj, ids, name, user=None, offset=0, context=None, values=None):
        if not context:
            context = {}
        if not values:
             values = {}
        res = {}
        for id in ids:
            res[id] = []
        for id in ids:
            query = "select project_id from dm_campaign where id = %i" %id
            cr.execute(query)
            project_ids = [ x[0] for x in cr.fetchall()]
            if name[0] == 'd':
                ids2 = obj.pool.get(self._obj).search(cr, user, [(self._fields_id,'in',project_ids),('type','=','DTP')], limit=self._limit)
            elif name[0] == 'm':
                ids2 = obj.pool.get(self._obj).search(cr, user, [(self._fields_id,'in',project_ids),('type','=','Mailing Manufacturing')], limit=self._limit)
            elif name[0] == 'c':
                ids2 = obj.pool.get(self._obj).search(cr, user, [(self._fields_id,'in',project_ids),('type','=','Customers List')], limit=self._limit)
            elif name[0] == 'i':
                ids2 = obj.pool.get(self._obj).search(cr, user, [(self._fields_id,'in',project_ids),('type','=','Items Procurement')], limit=self._limit)
            else :
                ids2 = obj.pool.get(self._obj).search(cr, user, [(self._fields_id,'in',project_ids),('type','=','Mailing Manufacturing')], limit=self._limit)
            for r in obj.pool.get(self._obj)._read_flat(cr, user, ids2, [self._fields_id], context=context, load='_classic_write'):
                res[id].append( r['id'] )
        return res #}}}

class dm_campaign(osv.osv):#{{{
    _inherit = "dm.campaign"
    _columns = {
        'project_id' : fields.many2one('project.project', 'Project', readonly=True,
            help="Generating the Retro Planning will create and assign the different tasks used to plan and manage the campaign"),
        'dtp_state' : fields.selection([('pending','Pending'),('inprogress','In Progress'),('done','Done')], 'DTP Status',readonly=True),
        'items_state' : fields.selection([('pending','Pending'),('inprogress','In Progress'),('done','Done')], 'Items Status',readonly=True),
        'manufacturing_state' : fields.selection([('pending','Pending'),('inprogress','In Progress'),('done','Done')], 'Manufacturing Status',readonly=True),
        'customer_file_state' : fields.selection([('pending','Pending'),('inprogress','In Progress'),('done','Done')], 'Customers Files Status',readonly=True),
        'dtp_task_ids': one2many_mod_task('project.task', 'project_id', "DTP tasks",
                                                        domain=[('type','ilike','DTP')], context={'type':'DTP'}),
        'manufacturing_task_ids': one2many_mod_task('project.task', 'project_id', "Manufacturing tasks",
                                                        domain=[('type','ilike','Mailing Manufacturing')],context={'type':'Mailing Manufacturing'}),
        'cust_file_task_ids': one2many_mod_task('project.task', 'project_id', "Customer Files tasks",
                                                        domain=[('type','ilike','Customers List')], context={'type':'Customers List'}),
        'item_task_ids': one2many_mod_task('project.task', 'project_id', "Items Procurement tasks",
                                                        domain=[('type','ilike','Items Procurement')], context={'type':'Items Procurement'}),
    }
    _defaults = {
        'manufacturing_state': lambda *a: 'pending',
        'items_state': lambda *a: 'pending',
        'customer_file_state': lambda *a: 'pending',
        'dtp_state': lambda *a: 'pending',
    }

    def manufacturing_state_inprogress_set(self, cr, uid, ids, *args):
        for id in self.browse(cr,uid,ids):
            if (id.state == 'draft') or (id.state == 'pending'):
                self.write(cr, uid, ids, {'manufacturing_state':'inprogress'})
            else:
                raise osv.except_osv("Error","This state cannot be set back to 'In Progress' once the campaign is opened")
        return True

    def dtp_state_inprogress_set(self, cr, uid, ids, *args):
        for id in self.browse(cr,uid,ids):
            if (id.state == 'draft') or (id.state == 'pending'):
                self.write(cr, uid, ids, {'dtp_state':'inprogress'})
            else:
                raise osv.except_osv("Error","This state cannot be set back to 'In Progress' once the campaign is opened")
        return True
 
    def customer_file_state_inprogress_set(self, cr, uid, ids, *args):
        for id in self.browse(cr,uid,ids):
            if (id.state == 'draft') or (id.state == 'pending'):
                self.write(cr, uid, ids, {'customer_file_state':'inprogress'})
            else:
                raise osv.except_osv("Error","This state cannot be set back to 'In Progress' once the campaign is opened")
        return True       
    
    def items_state_inprogress_set(self, cr, uid, ids, *args):
        for id in self.browse(cr,uid,ids):
            if (id.state == 'draft') or (id.state == 'pending'):
                self.write(cr, uid, ids, {'items_state':'inprogress'})
            else:
                raise osv.except_osv("Error!!","This state cannot be set back to 'In Progress' once the campaign is opened")
        return True 
    
    def manufacturing_state_done_set(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'manufacturing_state':'done'})
        return True
    
    def dtp_state_done_set(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'dtp_state':'done'})
        return True

    def customer_file_state_done_set(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'customer_file_state':'done'})
        return True
    
    def items_state_done_set(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'items_state':'done'})
        return True

dm_campaign()

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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: