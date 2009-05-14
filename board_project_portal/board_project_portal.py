# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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
from osv import fields,osv

import tools.sql

AVAILABLE_STATES = [
    ('draft','Draft'),
    ('open','Open'),
    ('cancel', 'Cancelled'),
    ('done', 'Closed'),
    ('pending','Pending')
]

class report_crm_case_state(osv.osv):
    _name = "report.crm.case.state"
    _description = "Cases by state"
    _auto = False
    _columns = {
        'section_id':fields.many2one('crm.case.section', 'Section', readonly=True, domain="[('name','ilike','Bug Tracking')]"),
        'nbr': fields.integer('# of Cases', readonly=True),
        'state': fields.selection(AVAILABLE_STATES, 'State', size=16, readonly=True),        
                }
    _order = 'state, section_id'
    
    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, "report_crm_case_state")
        cr.execute("""
              create view report_crm_case_state as (
                select
                    min(c.id) as id,
                    c.state,
                    c.section_id,
                    count(*) as nbr
                from
                    crm_case c
                where c.section_id is not null
                group by c.state, c.section_id)""")

report_crm_case_state()
