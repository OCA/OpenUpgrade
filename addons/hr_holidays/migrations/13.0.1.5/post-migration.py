# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_request_hour_mapping = [
    (-1, '0.5'),
    (-2, '1.5'),
    (-3, '2.5'),
    (-4, '3.5'),
    (-5, '4.5'),
    (-6, '5.5'),
    (-7, '6.5'),
    (-8, '7.5'),
    (-9, '8.5'),
    (-10, '9.5'),
    (-11, '10.5'),
    (-12, '11.5'),
    (-13, '12.5'),
    (-14, '13.5'),
    (-15, '14.5'),
    (-16, '15.5'),
    (-17, '16.5'),
    (-18, '17.5'),
    (-19, '18.5'),
    (-20, '19.5'),
    (-21, '20.5'),
    (-22, '21.5'),
    (-23, '22.5'),
    (-24, '23.5')
]

_unlink_by_xmlid = [
    'hr_holidays.mt_department_leave_allocation_approved',
    'hr_holidays.mt_department_leave_allocation_refused',
    'hr_holidays.mt_department_leave_approved',
    'hr_holidays.mt_department_leave_refused',
    'hr_holidays.mt_leave_allocation_refused',
    'hr_holidays.mt_leave_refused',
]


def assign_employee_leave_manager(env):
    """Asign as default leave manager the employee responsible, which is the
    one assigned by Odoo itself, and add them to the proper group, also
    following Odoo's logic.

    This is because although the field is not strictly required, all the
    approval logic needs it implicitly, and Odoo has put code in create/write
    methods for being sure a value is set.
    """
    openupgrade.logged_query(
        env.cr,
        """UPDATE hr_employee he
        SET leave_manager_id = he_parent.user_id
        FROM hr_employee he_parent
        WHERE he_parent.id = he.parent_id AND he.leave_manager_id IS NULL""",
    )
    leave_managers = env["hr.employee"].search([]).mapped("leave_manager_id")
    approver_group = env.ref(
        "hr_holidays.group_hr_holidays_responsible", raise_if_not_found=False,
    )
    if approver_group:
        approver_group.sudo().write({
            'users': [(4, x) for x in leave_managers.ids]
        })


def map_hr_leave_request_hour_from(cr):
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('request_hour_from'),
        'request_hour_from',
        _request_hour_mapping,
        table='hr_leave')


def map_hr_leave_request_hour_to(cr):
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('request_hour_to'),
        'request_hour_to',
        _request_hour_mapping,
        table='hr_leave')


def fill_leave_allocation_allocation_type(cr):
    """Switch type for accruals. The rest already have the proper type (default)."""
    openupgrade.logged_query(
        cr, """
        UPDATE hr_leave_allocation
        SET allocation_type = 'accrual'
        WHERE {accrual}
        """.format(accrual=openupgrade.get_legacy_name('accrual'))
    )


@openupgrade.migrate()
def migrate(env, version):
    assign_employee_leave_manager(env)
    map_hr_leave_request_hour_from(env.cr)
    map_hr_leave_request_hour_to(env.cr)
    fill_leave_allocation_allocation_type(env.cr)
    openupgrade.delete_records_safely_by_xml_id(env, _unlink_by_xmlid)
    openupgrade.load_data(env.cr, 'hr_holidays', 'migrations/13.0.1.5/noupdate_changes.xml')
