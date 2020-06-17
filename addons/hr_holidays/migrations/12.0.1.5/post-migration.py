# Copyright 2019 Eficent <http://www.eficent.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
from psycopg2 import sql
from psycopg2.extensions import AsIs


def fill_hr_holidays_dates(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE hr_holidays
        SET date_from = COALESCE(date_from, create_date)""",
    )
    openupgrade.logged_query(
        cr, """
        UPDATE hr_holidays
        SET date_to = COALESCE(date_to, create_date)""",
    )


def fill_hr_leave_type_validation_type(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE hr_leave_type
        SET validation_type = 'both'
        WHERE %s""",
        (AsIs(openupgrade.get_legacy_name('double_validation')), ),
    )


def fill_hr_leave_type_allocation_type(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE hr_leave_type
        SET allocation_type = 'no'
        WHERE %s""", (AsIs(openupgrade.get_legacy_name('limit')), ),
    )


def _move_model_in_data(env, ids, old_model, new_model):
    renames = [
        ('mail_message', 'model', 'res_id'),
        ('mail_followers', 'res_model', 'res_id'),
        ('ir_attachment', 'res_model', 'res_id'),
        ('mail_activity', 'res_model', 'res_id'),
        ('ir_model_data', 'model', 'res_id'),
    ]
    for rename in renames:
        openupgrade.logged_query(
            env.cr, """
            UPDATE %s
            SET %s = %s
            WHERE %s IN %s AND %s = %s""",
            (
                AsIs(rename[0]),
                AsIs(rename[1]), new_model,
                AsIs(rename[2]), tuple(ids), AsIs(rename[1]), old_model,
            ),
        )


def fill_hr_leave(env):
    # In pre-migration the hr_leave table still doesn't exist
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO hr_leave (
            id, category_id, date_from, date_to, department_id,
            employee_id, first_approver_id, holiday_status_id, holiday_type,
            manager_id, meeting_id, name, notes, number_of_days,
            payslip_status, report_note, second_approver_id, state, user_id,
            create_uid, create_date, write_uid, write_date
        )
        SELECT id, category_id, date_from, date_to, department_id, employee_id,
            first_approver_id, holiday_status_id, holiday_type, manager_id,
            meeting_id, name, notes, number_of_days, payslip_status,
            report_note, second_approver_id, state, user_id, create_uid,
            create_date, write_uid, write_date
        FROM hr_holidays
        WHERE %s = 'remove'
        RETURNING id""", (AsIs(openupgrade.get_legacy_name('type')), ),
    )
    ids = [x[0] for x in env.cr.fetchall()]
    if ids:
        _move_model_in_data(env, ids, 'hr.holidays', 'hr.leave')


def restore_resource_calendar_leave_link(env):
    """We set this now from the renamed column as can't be done previously
    or we will get fkey violation.
    """
    openupgrade.logged_query(
        env.cr, sql.SQL(
            """UPDATE resource_calendar_leaves SET holiday_id = {}
            WHERE holiday_id IS NULL"""
        ).format(
            sql.Identifier(openupgrade.get_legacy_name("holiday_id"))
        )
    )


def fill_hr_leave_request_dates(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE hr_leave
        SET request_date_from = COALESCE(request_date_from, date_from)"""
    )
    openupgrade.logged_query(
        cr, """
        UPDATE hr_leave
        SET request_date_to = COALESCE(request_date_to, date_to)"""
    )


def fill_hr_leave_allocation(env):
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO hr_leave_allocation (
            id, category_id, date_from, date_to,
            department_id, employee_id, first_approver_id, holiday_status_id,
            holiday_type, name, notes, number_of_days, second_approver_id,
            state, create_uid, create_date, write_uid, write_date)
        SELECT id, category_id, date_from, date_to, department_id, employee_id,
            first_approver_id, holiday_status_id, holiday_type, name, notes,
            number_of_days, second_approver_id, state, create_uid,
            create_date, write_uid, write_date
        FROM hr_holidays
        WHERE %s = 'add'
        RETURNING id""", (AsIs(openupgrade.get_legacy_name('type')), ),
    )
    ids = [x[0] for x in env.cr.fetchall()]
    if ids:
        _move_model_in_data(env, ids, 'hr.holidays', 'hr.leave.allocation')


def set_max_sequences(env):
    """Set for both new tables the next id val as the maximum of the previous
    table + 1. This way, we don't have any of the old IDs duplicated in new
    tables.
    """
    openupgrade.logged_query(
        env.cr,
        "SELECT setval('hr_leave_id_seq', (SELECT MAX(id) FROM hr_holidays))"
    )
    openupgrade.logged_query(
        env.cr,
        "SELECT setval('hr_leave_allocation_id_seq', "
        "(SELECT MAX(id) FROM hr_holidays))"
    )


def subscribe_new_subtypes(env):
    """Subscribe to the new subtypes to those that were subscribed to the
    old ones.
    """
    subtype_mapping = [
        ('mt_department_holidays_approved',
         ['mt_department_leave_allocation_approved',
          'mt_department_leave_approved']),
        ('mt_department_holidays_refused',
         ['mt_department_leave_allocation_refused',
          'mt_department_leave_refused']),
        ('mt_holidays_approved',
         ['mt_leave_allocation_approved',
          'mt_leave_approved']),
        ('mt_holidays_refused',
         ['mt_leave_allocation_refused',
          'mt_leave_refused']),
    ]
    for old, new in subtype_mapping:
        old_id = env.ref('hr_holidays.' + old).id
        for i, model in enumerate(['hr.leave.allocation', 'hr.leave']):
            new_id = env.ref('hr_holidays.' + new[i]).id
            openupgrade.logged_query(
                env.cr, """
                UPDATE mail_followers_mail_message_subtype_rel rel
                SET mail_message_subtype_id = %s
                FROM mail_followers mf, mail_message_subtype mms
                WHERE mf.id = rel.mail_followers_id
                    AND mms.id = rel.mail_message_subtype_id
                    AND mms.res_model = 'hr.holidays'
                    AND mf.res_model = %s
                    AND rel.mail_message_subtype_id = %s
                """, (new_id, model, old_id, )
            )


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    fill_hr_holidays_dates(cr)
    fill_hr_leave_type_validation_type(cr)
    fill_hr_leave_type_allocation_type(cr)
    fill_hr_leave(env)
    restore_resource_calendar_leave_link(env)
    fill_hr_leave_request_dates(cr)
    fill_hr_leave_allocation(env)
    set_max_sequences(env)
    openupgrade.load_data(
        cr, 'hr_holidays', 'migrations/12.0.1.5/noupdate_changes.xml')
    subscribe_new_subtypes(env)
    openupgrade.delete_records_safely_by_xml_id(
        env, [
            'hr_holidays.mt_department_holidays_approved',
            'hr_holidays.mt_department_holidays_confirmed',
            'hr_holidays.mt_department_holidays_first_validated',
            'hr_holidays.mt_department_holidays_refused',
            'hr_holidays.mt_holidays_approved',
            'hr_holidays.mt_holidays_confirmed',
            'hr_holidays.mt_holidays_first_validated',
            'hr_holidays.mt_holidays_refused',
        ],
    )
