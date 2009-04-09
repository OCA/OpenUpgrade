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

from mx import DateTime
import time
from osv import fields, osv
import tools

class md_hr_address_street(osv.osv):
    _name = "md.hr.address.street"
    _description = "Street"
    _columns = {
                'name' : fields.char("Street", size=80,select=1),
                
                }
md_hr_address_street()

class md_hr_address_zip(osv.osv):
    _name = "md.hr.address.zip"
    _description = "Zip"
    _columns = {
                'name' : fields.char("Zip", size=16,select=1),
                
                }
    
md_hr_address_zip()

class md_hr_address_town(osv.osv):
    _name = "md.hr.address.town"
    _description = "Town"
    _columns = {
                'name' : fields.char("Town", size=16,select=1),
                
                }
    
md_hr_address_town()

class md_hr_address(osv.osv):
     _name = "md.hr.address"
     _description = "Employee Address"
     _columns = {
                 'employee_id' : fields.many2one("hr.employee", "Employee"), 
                 'type': fields.selection([('default','Default'),('invoice','Invoice'),('contact','Contact')],'Address Type'),
                 'name' : fields.char("Name", size=80),
                 'street_id' : fields.many2one("md.hr.address.street", "Street"),
                 'house_nbr' : fields.char("# House No", size=16),
                 'zip_id' : fields.many2one("md.hr.address.zip", "Zip"),
                 'town_id' : fields.many2one("md.hr.address.town", "Town"),
                 'country_id' : fields.many2one("res.country", "Country"),
                  
                            
                 }
md_hr_address()

class hr_employee_max_travel_allow(osv.osv):
     _name = "hr.employee.max.travel.allow"
     _description = "Maximun Travel allowance per year and per day"
     _columns = {
                 'amount_per_day' : fields.float("Maximun Amount Per Day",required=True),
                 'amount_per_year' : fields.float("Maximum Amount Per Year",required=True),
                 }
   
hr_employee_max_travel_allow()

class hr_employee(osv.osv):
    
    def _expressed_by_year(self, cr, uid, ids, field_name, arg, context): 
        res = {}
        for emp in self.browse(cr, uid, ids):
            data=self.pool.get('hr.employee.max.travel.allow')
            ids = data.search(cr, uid, [])
            vals = data.read(cr, uid, ids, ['amount_per_day', 'amount_per_year'], context)
            print"::VALS::",vals
            for val in vals:
                M = val['amount_per_year']
                A = val['amount_per_day']
            print"::M::",M
            print"::A::",A
#            M = 50000
#            A = 50
            dist_home_work =  emp.dist_home_work and emp.dist_home_work or 1.0
            cr.execute("""
                      select count(tmp.*) as no_of_days from hr_employee as hr_emp left outer join (
                             select hremp.id as emp_id,count(*) as no_of_days from md_hr_contract_availability as hrcon_avail
                                    inner join hr_contract as hrcon on hrcon.id = hrcon_avail.contract_id
                                    inner join hr_employee as hremp on hrcon.employee_id = hremp.id
                                    group by hremp.id,hrcon_avail.day) as tmp on hr_emp.id = tmp.emp_id
                            where hr_emp.id = %d
                            group by hr_emp.id
                            order by hr_emp.id
                      """%(emp.id))
            tmp = cr.fetchone()
            number_of_workdays_per_week = tmp[0] and tmp[0] or 0
            if number_of_workdays_per_week and dist_home_work:
               res[emp.id] = min( A * dist_home_work * number_of_workdays_per_week * 52 , M )
               print"res[emp.id]",res[emp.id]
            else:
               res[emp.id] = 0.0
        return res
         
    _name = "hr.employee"
    _description = "Employee"
    _inherit = "hr.employee"
    _columns = {
                'code' : fields.char("Personal Number", size=8),
                'firstname' : fields.char("Surname", size=80),
#                'lasname' : fields.char("Name", size=80,required="True"),
                'prefix' : fields.char("Prefix", size=16),
                'birthdate' : fields.date("Date of Birthday"),   
                'nationality_id' : fields.many2one("res.country", "Nationality",select=True), 
                'gender': fields.selection([('male','Male'),('female','Female')],'Gender'), 
                'addres_id' : fields.many2one("md.hr.address", "Address"), 
                'address_number' : fields.char("Number", size=8), 
                'zip_id' : fields.many2one("md.hr.address.zip", "Zip"),
                'town_id' : fields.many2one("md.hr.address.town", "Town"),
                'country_id' : fields.many2one("res.country", "Country"),
                'phone' : fields.char("Phone Number", size=16),
                'mobile' : fields.char("Mobile Phone Number", size=16),
                'email' : fields.char("Email", size=256), 
                'maiden_name' : fields.char("Maiden Name", size=80), 
                'marital_status': fields.selection([('single','Single'),('married','Married')],'Marital Status'),
                'nbr_of_children' : fields.integer("# of children", size=8),
                'partner_firstname' : fields.char("Partner's surname", size=80),
                'partner_lastname' : fields.char("Partner's name", size=80),
                'partner_prefix' : fields.char("Partner's prefix", size=16), 
                'partner_initials' : fields.char("Partner's initials", size=8), 
                'partner_dob' : fields.date("Partner's DOB"),   
                'partner_gender': fields.selection([('male','Male'),('female','Female')],"Partner's gender"), 
                'nin' : fields.char("National Insurance Number", size=26),
                'education' : fields.char("Education", size=80),
                'field_of_education' : fields.char("Field of education", size=80), 
                'travel_allowance' : fields.boolean("Travel Allowande"), 
                'dist_home_work' : fields.integer("Dist. between home and workplace (km)", size=8),
                'amount_travel_allowance' : fields.function(_expressed_by_year, method=True, string="Travel allowance(per year)",readonly=True),
                'pension' : fields.boolean("Pension"), 
                'pension_waiver' : fields.boolean("Pension waiver"), 
                'waowiaww' : fields.boolean("Disability/unemployment benefit"),
                'waowiaww_dep_id':fields.many2one('hr.department','If yes, which department'),
                'attachment_earings_order' : fields.boolean("Attachment of earings order",),
                'earings_order_beneficier' : fields.char("In name of", size=80,readonly=False),
                'earings_order_amount' : fields.float("Amount"),
                'earings_order_account' : fields.char("Account Number",size=16),
                'spaarloonregeling' : fields.float("Spaarloonregeling"),
                'spaarloonregeling_account' : fields.char("A/C number spaarloonregeling",size=16),
                'levensloopregeling' : fields.float("Levensloopregeling"),
                'levensloopregeling_account' : fields.char("A/C number levensloonregeling",size=16),
                'evaluation_id': fields.one2many('hr_evaluation.evaluation', 'employee_id'),
                'holidays_id': fields.one2many('hr.holidays', 'employee_id'),          
                }
   
    
    def on_change_nbr_of_children(self,cr, uid, ids, nbr_of_children,context=None):   
        if nbr_of_children < 0:
            raise osv.except_osv(
                        'Please Enter Value > 0!!!!','# of children')
            return {'value':{'nbr_of_children':0}}
        return {}
    
    def on_change_dist_home_work(self,cr, uid, ids, dist_home_work,context=None):   
        if dist_home_work < 0:
            raise osv.except_osv(
                        'Please Enter Value > 0!!!!','Dist. between home and workplace (km)')
            return {'value':{'dist_home_work':0}}
        return {}
    
hr_employee()







  
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

