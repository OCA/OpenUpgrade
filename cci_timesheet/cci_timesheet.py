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

cci_timesheet()

class cci_timesheet_line(osv.osv):


    def _get_diff_hours(self, cr, uid, ids, name, args, context=None):
        res={}
        for line in self.browse(cr, uid, ids, context):
            res[line.id] = line.hour_to - line.hour_from
        print "res: ", res
        return res

    #TODO: by default, the grant_id should be the grant defined on the timesheet 

    _name="cci_timesheet.line"
    _description="CCI Timesheet Line"

    _columns = {
        'name': fields.char('Name', size=128, required=True),
        'day_date' : fields.date('Date of the Day', required=True),
        'hour_from' : fields.float('Hour From', required=True),
        'hour_to' : fields.float('Hour To',required=True),
        'user_id': fields.many2one('res.users', 'User', required=True),
        'grant_id': fields.many2one('cci_timesheet.grant', 'Grant', required=True),
        'timesheet_id': fields.many2one('cci.timesheet', 'Timesheet', ondelete='cascade'),
        'zip_id': fields.many2one('res.partner.zip', 'Zip'),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'contact_id': fields.many2one('res.partner.contact', 'Contact'),
        'description': fields.text('Description'),
        'suppl_cost' : fields.float('Supplementary Cost',digits=(16,2)),
        'kms' : fields.integer('Kilometers'),
        'diff_hours' : fields.function(_get_diff_hours, method=True, string='Hour To - Hour From',type='float'),
    }

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





#	_columns = {
#		'user_id' : fields.char('Employee',size=32),
#		'grant_id' :fields.char('Grant',size=32),
#		'th_hours_per_week' :fields.float('Hours/Week (Th)'),
#		'th_percentage' : fields.float('% (Th)'),
#		'prac_hours_per_week' :fields.float('Hours/Week (Prac)'),
#		'prac_percentage' : fields.float('% (Prac)'),
#		'date_from': fields.date('From Date'),
##		'date_to': fields.date('To Date'),
#		}
#	def init(self, cr):
#		cr.execute("""
#			create or replace view report_timesheet_affectation as (
#			SELECT 	temp.user_id as user_id, 
#					temp.grant_id as grant_id, 
#					temp.th_hours_per_week as th_hours_per_week,
#					temp.th_percentage as th_percentage,
#					temp.prac_hours_per_week as prac_hours_per_week,
#					0 as prac_percentage,
#					temp
#			FROM
#			(	SELECT 	users.name as user_id, 
#						affect.grant_id as grant_id, 
#						SUM(affect.hours_per_week) as th_hours_per_week,
#						SUM(affect.percentage) as th_percentage,
#						SUM(line.hour_to - line.hour_from) as prac_hours_per_week
#				FROM res_users users 
##				LEFT JOIN cci_timesheet_affectation affect on (affect.user_id = users.id)
#				LEFT JOIN cci_timesheet_line line on (line.grant_id = affect.grant_id)
	#			GROUP BY users.name, affect.grant_id
#			) as temp,


#			)""")


#good one:
#select users.name as user_id, affect.grant_id as grant_id, SUM(affect.hours_per_week) as th_hours_per_week,SUM(affect.percentage) as th_percentage from res_users users LEFT JOIN cci_timesheet_affectation affect on (affect.user_id = users.id) group by users.name, grant_id;



#test one:
#SELECT users.name as user_id, affect.grant_id as grant_id, SUM(affect.hours_per_week) as th_hours_per_week, SUM(affect.percentage) as th_percentage, SUM(line.hour_to - line.hour_from) as prac_hours_per_week FROM res_users users LEFT JOIN cci_timesheet_affectation affect on (affect.user_id = users.id) LEFT JOIN cci_timesheet_line line on (line.grant_id = affect.grant_id) GROUP BY users.name, affect.grant_id;

report_timesheet_affectation()
