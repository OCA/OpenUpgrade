# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Sylvain LE GAL
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

from openupgrade import openupgrade, openupgrade_70
from openerp import pooler, SUPERUSER_ID


def migrate_hr_employee_addresses(cr, pool):
    """
    Change reference to old res_partner_address to new res_partner
    """
    # 'address_home_id' is now a 'res.partner' object
    openupgrade_70.set_partner_id_from_partner_address_id(
        cr, pool, 'hr.employee',
        'address_home_id', openupgrade.get_legacy_name('address_home_id'))
    # 'address_id' is now a 'res.partner' object
    openupgrade_70.set_partner_id_from_partner_address_id(
        cr, pool, 'hr.employee',
        'address_id', openupgrade.get_legacy_name('address_id'))


def migrate_hr_employee_department(cr, pool):
    """
    Update 'hr_employee.department_id' with value from deleted
    res_users.context_department_id.
    """
    hr_employee_obj = pool.get('hr.employee')
    cr.execute("""
        SELECT
            hr_emp.id as hr_emp_id,
            res_users.context_department_id as dep_id
        FROM hr_employee hr_emp
        INNER JOIN resource_resource res_res ON hr_emp.resource_id = res_res.id
        INNER JOIN res_users  ON res_res.user_id = res_users.id
        WHERE hr_emp.department_id is null
        AND NOT res_users.context_department_id is null""")
    for (hr_emp_id, dep_id) in cr.fetchall():
        vals = {
            'department_id': dep_id,
            }
        hr_employee_obj.write(cr, SUPERUSER_ID, hr_emp_id, vals)


def migrate_hr_job(cr):
    """
    Change obsolete selection values for hr_job.state
    """
    openupgrade.logged_query(
        cr, "UPDATE hr_job SET state = 'open' WHERE state = 'old' ")


def replace_user_partner(cr, pool):
    """
    If there's a sensible partner (address_id) to use for the user record,
    do that instead of using the newly created one.
    Don't use address_id if it points to a company's partner.
    """
    root_partner_id = pool['ir.model.data'].get_object_reference(
        cr, SUPERUSER_ID, 'base', 'partner_root')[1]
    cr.execute(
        '''UPDATE res_users SET partner_id=u.partner_id
        FROM (
            SELECT
            r.user_id, e.address_id partner_id
            FROM hr_employee e
            JOIN resource_resource r ON e.resource_id=r.id
            WHERE r.user_id IS NOT NULL
            AND e.address_id IS NOT NULL
            AND e.address_id NOT IN
                (SELECT partner_id FROM res_company)) u
        WHERE
        (
            res_users.partner_id IS NULL or
            res_users.partner_id=openupgrade_7_created_partner_id
        )
        AND u.user_id=res_users.id AND res_users.partner_id <> %s
        RETURNING id, openupgrade_7_created_partner_id''',
        (root_partner_id,))
    updated_user_ids = dict((k, v) for k, v in cr.fetchall())
    if not updated_user_ids:
        return
    cr.execute(
        '''UPDATE res_partner
        SET lang=p.lang, tz=p.tz
        FROM res_partner p, res_users u
        WHERE p.id=u.openupgrade_7_created_partner_id AND
        u.partner_id=res_partner.id''')
    cr.execute(
        '''UPDATE res_users
        SET openupgrade_7_created_partner_id=NULL
        WHERE id in %s AND partner_id <> %s''',
        (tuple(updated_user_ids.keys()), root_partner_id))
    cr.execute(
        'DELETE FROM res_partner p where id in %s and id <> %s',
        (tuple(updated_user_ids.values()), root_partner_id))


def amend_user_partner(cr, pool):
    """
    For newly created user partners, amend some data from the employee record
    if available
    """
    cr.execute(
        '''UPDATE res_partner p SET
        mobile=e.mobile_phone,
        phone=e.work_phone,
        email=e.work_email,
        image=e.image,
        name=r.name
        FROM
        hr_employee e
        JOIN resource_resource r ON e.resource_id=r.id
        JOIN res_users u ON r.user_id=u.id
        WHERE
        u.partner_id=p.id AND
        u.partner_id=u.openupgrade_7_created_partner_id''')


@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    migrate_hr_employee_addresses(cr, pool)
    migrate_hr_employee_department(cr, pool)
    migrate_hr_job(cr)
    replace_user_partner(cr, pool)
    amend_user_partner(cr, pool)
