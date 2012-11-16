# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2012 Therp BV (<http://therp.nl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import pooler, logging
from openerp.openupgrade import openupgrade

logger = logging.getLogger('OpenUpgrade')

@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    #null values of the many2one are reset to first value in the selection, 
    #restore the null values
    cr.execute('update hr_employee set marital=NULL where '+
        openupgrade.get_legacy_name('marital')+' is NULL')
    #get possible marital states and if in the original many2one, update 
    #selection field
    marital_states={}
    for (marital_state,marital_state_name) in pool.get('hr.employee')._columns['marital'].selection:
        cr.execute(
            'update hr_employee set marital=%(marital_state)s where '+
            openupgrade.get_legacy_name('marital')+' in'+
            '(select id from '+
            openupgrade.get_legacy_name('hr_employee_marital_status')+
            ' where lower(name) in %(marital_states)s)',            
            {
                'marital_state': marital_state, 
                'marital_states': 
                    tuple([marital_state.lower(),marital_state_name.lower()])
            })
        marital_states[marital_state]=marital_state_name
        
    #get marital states not included in the selection
    cr.execute(
        'select id from hr_employee where '+
        openupgrade.get_legacy_name('marital')+' is not null and '+
        openupgrade.get_legacy_name('marital')+' not in '+
        '(select id from '+
            openupgrade.get_legacy_name('hr_employee_marital_status')+
            ' where lower(name) in %(marital_states)s)',
        {
            'marital_states': 
                tuple(
                    [v.lower() for v in marital_states.itervalues()]+
                    [k.lower() for k in marital_states.iterkeys()])
        })
    if cr.rowcount:
        logger.warning('not all values of hr_employee_marital_status are in '+
            'the selection. review hr_employee ids %s', 
            [row[0] for row in cr.fetchall()])
    else:
        logger.info('all values of hr_employee_marital_status are in the selection')
        openupgrade.drop_columns(
            cr, 
            [('hr_employee', 
                openupgrade.get_legacy_name('marital'))])
        cr.execute('drop table '+
            openupgrade.get_legacy_name('hr_employee_marital_status'))

    #fields have been calculated already
    cr.execute(
        'update hr_job set no_of_recruitment='+
        openupgrade.get_legacy_name('expected_employees')+
        '-no_of_employee')
    #recalculate expectred employees
    cr.execute(
        'update hr_job set expected_employees=no_of_recruitment+no_of_employee')
    openupgrade.drop_columns(
            cr, 
            [(
                'hr_job', 
                openupgrade.get_legacy_name('expected_employees')
            )])
    openupgrade.load_data(cr, 'hr', 'migrations/6.1.1.1/data/hr_security.xml')
