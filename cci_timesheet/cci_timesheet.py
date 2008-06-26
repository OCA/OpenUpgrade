import time
import pooler
from osv import fields, osv

class cci_timesheet_grant(osv.osv):

    _name="cci_timesheet.grant"
    _description="CCI Timesheet Grant"
    _columns = {
        'name': fields.char('Grant Name', size=128, required=True),
    }
cci_timesheet_grant()

class cci_timesheet(osv.osv):

    _name="cci.timesheet"
    _description="CCI Timesheet"

    _columns = {
        'name': fields.char('Name', size=128, required=True),
        'date_from' : fields.date('From Date', required=True),
        'date_to' : fields.date('To Date', required=True),
        'grant_id': fields.many2one('cci_timesheet.grant', 'Grant', required=True),
        'state': fields.selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('validated', 'Validated')], 'State', readonly=True, required=True),
        'sending_date' : fields.date('Sending Date'),
        'asked_amount' : fields.float('Asked Amount',digits=(16,2)),
        'accepted_amount' : fields.float('Accepted Amount',digits=(16,2)),
        'line_ids': fields.one2many('cci_timesheet.line', 'timesheet_id', 'Timesheet Lines'),
    }
    _defaults = {
        'state' : lambda *a: 'draft',
    }
cci_timesheet()

class cci_timesheet_line(osv.osv):
    _name="cci_timesheet.line"
    _description="CCI Timesheet Line"

    _columns = {
        'name': fields.char('Name', size=128, required=True),
        'day_date' : fields.date('Date of the Day', required=True),
        'hour_from' : fields.float('Hour From', size=8, required=True),
        'hour_to' : fields.float('Hour To', size=8, required=True),
        'user_id': fields.many2one('res.users', 'User', required=True),
        'grant_id': fields.many2one('cci_timesheet.grant', 'Grant', required=True),
        'timesheet_id': fields.many2one('cci.timesheet', 'Timesheet', ondelete='cascade'),
        'zip_id': fields.many2one('res.partner.zip', 'Zip'),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'contact_id': fields.many2one('res.partner.contact', 'Contact'),
        'description': fields.text('Description'),
        'suppl_cost' : fields.float('Supplementary Cost',digits=(16,2)),
        'kms' : fields.integer('Kilometers'),
    }

cci_timesheet_line()

class cci_timesheet_affectation(osv.osv):
    _name="cci_timesheet.affectation"
    _description="Timesheet Affectation"

    _columns = {
        'user_id': fields.many2one('res.users', 'User', required=True),
        'grant_id': fields.many2one('cci_timesheet.grant', 'Grant', required=True),
        'percentage' : fields.float('Percentage', digits=(16,2),required=True),
        'hours_per_week' : fields.float('Hours Per Week',size=8, required=True),
        'date_from' : fields.date('From Date', required=True),
        'date_to' : fields.date('To Date', required=True),
        'rate' : fields.float('Rate', digits=(16,2), required=True),

    }

cci_timesheet_affectation()