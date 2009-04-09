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
import pooler
from osv import fields, osv

class cci_timesheet_grant(osv.osv):

    _name="cci_timesheet.grant"
    _description="CCI Timesheet Grant"
    _columns = {
        'name': fields.char('Grant Name', size=128, required=True),
        'line_ids': fields.one2many('cci_timesheet.line', 'grant_id', 'Timesheet Lines',),
        'affectation_ids': fields.one2many('cci_timesheet.affectation', 'grant_id', 'Affectation Lines',),
    }
cci_timesheet_grant()

class cci_timesheet(osv.osv):

    _name="cci.timesheet"
    _description="CCI Timesheet"

    _columns = {
        'name': fields.char('Name', size=128, required=True,readonly=True,states={'draft':[('readonly',False)]}),
        'date_from' : fields.date('From Date', required=True,readonly=False,states={'validated':[('readonly',True)],'cancelled':[('readonly',True)]}),
        'date_to' : fields.date('To Date', required=True,readonly=False,states={'validated':[('readonly',True)],'cancelled':[('readonly',True)]}),
        'grant_id': fields.many2one('cci_timesheet.grant', 'Grant',readonly=True, required=True,states={'draft':[('readonly',False)]}),
        'state': fields.selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('validated', 'Validated'),('cancelled', 'Cancelled')], 'State', readonly=True, required=True),
        'sending_date' : fields.date('Sending Date'),
        'asked_amount' : fields.float('Asked Amount',digits=(16,2)),
        'accepted_amount' : fields.float('Accepted Amount',digits=(16,2)),
        'line_ids': fields.one2many('cci_timesheet.line', 'timesheet_id', 'Timesheet Lines',readonly=False,states={'validated':[('readonly',True)],'cancelled':[('readonly',True)]}),
    }
    _defaults = {
        'state' : lambda *a: 'draft',
    }

    def check_timesheet_line(self, cr, uid, ids):
        if not ids:
            return True
        for data in self.browse(cr, uid, ids):
            for lines in data.line_ids:
                if not lines.grant_id:
                    return False
                if (data.grant_id.id != lines.grant_id.id) or lines.day_date < data.date_from or lines.day_date > data.date_to:
                    return False
        return True

    def set_to_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'draft'})
        return True

    def set_to_validate(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'validated'})

        return True

    def set_to_confirm(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'confirmed'})
        return True

    def set_to_cancel(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'cancelled'})
        return True

    _constraints = [(check_timesheet_line, 'Warning: Date of Timesheet Line should be bewteen the Two dates of the Timesheet and Grant of Timesheet Line should be the same as the Timesheet', ['Timesheet lines'])]

cci_timesheet()

class cci_timesheet_line(osv.osv):


    def _get_diff_hours(self, cr, uid, ids, name, args, context=None):
        res={}
        for line in self.browse(cr, uid, ids, context):
            res[line.id] = line.hour_to - line.hour_from
        return res

    def check_timesheet(self, cr, uid, ids):
        if not ids:
            return True
        for lines in self.browse(cr, uid, ids):
            if lines.timesheet_id:
                if not lines.grant_id:
                    return False
                if (lines.timesheet_id.grant_id.id != lines.grant_id.id) or lines.day_date < lines.timesheet_id.date_from or lines.day_date > lines.timesheet_id.date_to:
                    return False
        return True

    #TODO: by default, the grant_id should be the grant defined on the timesheet

    _name="cci_timesheet.line"
    _description="CCI Timesheet Line"

    _columns = {
        'name': fields.char('Name', size=128, required=True),
        'day_date' : fields.date('Date of the Day', required=True),
        'hour_from' : fields.float('Hour From', required=True),
        'hour_to' : fields.float('Hour To',required=True),
        'user_id': fields.many2one('res.users', 'User', required=True),
        'grant_id': fields.many2one('cci_timesheet.grant', 'Grant',),
        'timesheet_id': fields.many2one('cci.timesheet', 'Timesheet', ondelete='cascade'),
        'zip_id': fields.many2one('res.partner.zip', 'Zip'),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'contact_id': fields.many2one('res.partner.contact', 'Contact'),
        'description': fields.text('Description'),
        'suppl_cost' : fields.float('Supplementary Cost',digits=(16,2)),
        'kms' : fields.integer('Kilometers'),
        'diff_hours' : fields.function(_get_diff_hours, method=True, string='Hour To - Hour From',type='float'),
    }
    _constraints = [(check_timesheet, 'Warning: Date of Timesheet Line should be bewteen the Two dates of the Timesheet and Grant of Timesheet Line should be the same as the Timesheet', ['Timesheet lines'])]
cci_timesheet_line()

class cci_timesheet_affectation(osv.osv):
    _name="cci_timesheet.affectation"
    _description="Timesheet Affectation"

    _columns = {
        'name': fields.char('Name', size=128, required=True),
        'user_id': fields.many2one('res.users', 'User', required=True),
        'grant_id': fields.many2one('cci_timesheet.grant', 'Grant', required=True),
        'percentage' : fields.float('Percentage', digits=(16,2),required=True),
        'hours_per_week' : fields.float('Hours Per Week',size=9, required=True),
        'date_from' : fields.date('From Date', required=True),
        'date_to' : fields.date('To Date', required=True),
        'rate' : fields.float('Rate', digits=(16,2), required=True),
    }

cci_timesheet_affectation()


class report_timesheet_affectation(osv.osv):
    _name = "report.timesheet.affectation"
    _description = "Report on Timesheet and Affectation"
    _auto = False
    _columns = {
        'name': fields.char('Name', size=128),
        'day_date' : fields.date('Date of the Day'),
        'hour_from' : fields.float('Hour From'),
        'hour_to' : fields.float('Hour To'),
        'user_name':  fields.char('Employee', size=32),
        'grant_name': fields.char('Grant', size=128),
        'timesheet_id': fields.integer('Timesheet Ref'),
        'description': fields.text('Description'),
        'diff_hours' : fields.float('Hours'),

        'affectation_name' : fields.char('Affectation', size=128),
        'th_percentage' : fields.float('Percentage'),
        'hours_per_week' : fields.float('Hours Per Week'),
        'date_from' : fields.date('From Date'),
        'date_to' : fields.date('To Date'),
        'rate' : fields.float('Rate'),
    }

    def init(self, cr):
        cr.execute("""
            create or replace view report_timesheet_affectation as (
            SELECT
                line.id as id,
                line.name as name,
                line.day_date as day_date,
                line.hour_from as hour_from,
                line.hour_to as hour_to,
                u.name as user_name,
                g.name as grant_name,
                line.timesheet_id as timesheet_id,
                line.description as description,
                (line.hour_to - line.hour_from) as diff_hours,
                affect.name as affectation_name,
                affect.percentage as th_percentage,
                affect.hours_per_week as hours_per_week,
                affect.date_from as date_from,
                affect.date_to as date_to,
                affect.rate as rate
            FROM
                cci_timesheet_line line,
                cci_timesheet_affectation affect,
                res_users u,
                cci_timesheet_grant g
            WHERE
                line.user_id = affect.user_id
                AND line.user_id = u.id
                AND line.grant_id = affect.grant_id
                AND line.grant_id = g.id
                AND (line.day_date <= affect.date_to AND line.day_date >= affect.date_from)
            )""")

report_timesheet_affectation()

class crm_case(osv.osv):

    _inherit = 'crm.case'
    _description = 'crm case'
    _columns = {
        'grant_id' : fields.many2one('cci_timesheet.grant','Grant'),
        'zip_id' : fields.many2one('res.partner.zip','Zip'),
        'timesheet_line_id':fields.many2one('cci_timesheet.line','Timesheet Line')
    }

    def onchange_partner_id(self, cr, uid, ids, part, email=False):
        data = super(crm_case, self).onchange_partner_id(cr, uid, ids, part, email)
        if not part:
            return data
        addr = self.pool.get('res.partner').address_get(cr, uid, [part])
        if addr['default']:
            data['value']['zip_id'] = self.pool.get('res.partner.address').browse(cr, uid, addr['default']).zip_id.id
        return data
crm_case()

class project_work(osv.osv):
    _inherit = "project.task.work"
    _description = "Task Work"

    def create(self, cr, uid, vals, *args, **kwargs):
        res = super(project_work, self).create(cr, uid, vals)
        self.write(cr, uid, [res], vals)
        return res

    def write(self, cr, uid, ids, vals, *args, **kwargs):
        res = {}
        if not ids:
            return res
        for work in self.browse(cr, uid, ids):
            if (not work.zip_id) and ('zip_id' not in vals or not vals['zip_id']):
                if work.task_id.project_id.partner_id:
                    temp = self.pool.get('res.partner').address_get(cr, uid, [work.task_id.project_id.partner_id.id])
                    vals['zip_id'] = self.pool.get('res.partner.address').browse(cr, uid, temp['default']).zip_id.id
            if (not work.partner_id) and ('partner_id' not in vals or not vals['partner_id']):
                if work.task_id.project_id.partner_id:
                    vals['partner_id'] = work.task_id.project_id.partner_id.id

            if (not work.contact_id) and ('contact_id' not in vals or not vals['contact_id']):
                if work.task_id.project_id.contact_id2:
                    vals['contact_id'] = work.task_id.project_id.contact_id2.id
        return super(project_work, self).write(cr, uid, ids, vals)


    _columns = {
        'grant_id' : fields.many2one('cci_timesheet.grant','Grant'),
        'zip_id' : fields.many2one('res.partner.zip','Zip'),
        'partner_id' : fields.many2one('res.partner','Partner'),
        'contact_id' : fields.many2one('res.partner.contact','Contact'),
        'timesheet_line_id':fields.many2one('cci_timesheet.line','Timesheet Line')
    }
    _defaults = {
#        'zip_id': _get_zip_id,
 #       'partner_id': _get_partner_id,
  #      'contact_id': _get_contact_id,
    }
project_work()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

