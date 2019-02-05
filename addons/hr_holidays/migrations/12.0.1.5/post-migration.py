# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
from psycopg2.extensions import AsIs


def fill_hr_holidays_dates(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE hr_holidays
        SET date_from = COALESCE(date_from, create_date)
        """
    )
    openupgrade.logged_query(
        cr, """
        UPDATE hr_holidays
        SET date_to = COALESCE(date_to, create_date)
        """
    )


def fill_hr_leave_type_validation_type(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE hr_leave_type
        SET validation_type = 'both'
        WHERE %s = TRUE
        """, (AsIs(openupgrade.get_legacy_name('double_validation')), ),
    )


def fill_hr_leave_type_allocation_type(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE hr_leave_type
        SET allocation_type = 'no'
        WHERE %s = TRUE
        """, (AsIs(openupgrade.get_legacy_name('limit')), ),
    )


def fill_hr_leave(env):
    # In pre-migration the hr_leave table still doesn't exist
    env.cr.execute(
        """
        ALTER TABLE hr_leave
        ADD COLUMN {} integer;
        """.format(openupgrade.get_legacy_name('holidays_id'))
    )
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO hr_leave (category_id, date_from, date_to, department_id,
            employee_id, first_approver_id, holiday_status_id, holiday_type,
            manager_id, meeting_id, name, notes, number_of_days,
            payslip_status, report_note, second_approver_id, state, user_id,
            create_uid, create_date, write_uid, write_date, %s)
        SELECT category_id, date_from, date_to, department_id, employee_id,
            first_approver_id, holiday_status_id, holiday_type, manager_id,
            meeting_id, name, notes, number_of_days, payslip_status,
            report_note, second_approver_id, state, user_id, create_uid,
            create_date, write_uid, write_date, id
        FROM hr_holidays
        WHERE %s = 'remove'
        RETURNING id, %s
        """, (
            AsIs(openupgrade.get_legacy_name('holidays_id')),
            AsIs(openupgrade.get_legacy_name('type')),
            AsIs(openupgrade.get_legacy_name('holidays_id')),
        ),
    )
    new_rows = env.cr.fetchall()
    # fix parent_id:
    openupgrade.logged_query(
        env.cr, """
        UPDATE hr_leave hl1
        SET parent_id = hl2.id
        FROM hr_holidays hh1
        INNER JOIN hr_holidays hh2 ON hh1.parent_id = hh2.id
        INNER JOIN hr_leave hl2 ON hh2.id = hl2.%s
        WHERE hl1.%s = hh1.id
        """, (
            AsIs(openupgrade.get_legacy_name('holidays_id')),
            AsIs(openupgrade.get_legacy_name('holidays_id')),
        ),
    )
    # update many2ones of other models
    env.cr.execute("""
        SELECT model, name
        FROM ir_model_fields
        WHERE relation = 'hr_leave' AND ttype = 'many2one'
            AND model NOT IN ('hr.holidays', 'hr.leave')
    """)
    for field in env.cr.fetchall():
        for row in new_rows:
            table = field[0].replace('.', '_')
            env.cr.execute(
                """
                UPDATE %s
                SET %s = %s
                WHERE %s = %s
                """ % (table, field[1], field[1], row[0], row[1])
            )
    # update mail_message
    openupgrade.logged_query(
        env.cr, """
        UPDATE mail_message mm
        SET model = 'hr.leave', res_id = hl.id
        FROM hr_leave hl
        WHERE mm.res_id = hl.%s AND mm.model = 'hr.holidays'
        """, (
            AsIs(openupgrade.get_legacy_name('holidays_id')),
        ),
    )
    # update mail_followers
    openupgrade.logged_query(
        env.cr, """
        UPDATE mail_followers mf
        SET res_model = 'hr.leave', res_id = hl.id
        FROM hr_leave hl
        WHERE mf.res_id = hl.%s AND mf.res_model = 'hr.holidays'
        """, (
            AsIs(openupgrade.get_legacy_name('holidays_id')),
        ),
    )
    # update attachments
    openupgrade.logged_query(
        env.cr, """
        UPDATE ir_attachment ia
        SET res_model = 'hr.leave', res_id = ia.id
        FROM hr_leave hl
        WHERE ia.res_id = hl.%s AND ia.res_model = 'hr.holidays'
        """, (
            AsIs(openupgrade.get_legacy_name('holidays_id')),
        ),
    )


def fill_hr_leave_request_dates(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE hr_leave
        SET request_date_from = COALESCE(request_date_from, date_from)
        """
    )
    openupgrade.logged_query(
        cr, """
        UPDATE hr_leave
        SET request_date_to = COALESCE(request_date_to, date_to)
        """
    )


def fill_hr_leave_allocation(env):
    # In pre-migration the hr_leave_allocation table still doesn't exist
    env.cr.execute(
        """
        ALTER TABLE hr_leave_allocation
        ADD COLUMN {} integer;
        """.format(openupgrade.get_legacy_name('holidays_id'))
    )
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO hr_leave_allocation (category_id, date_from, date_to,
            department_id, employee_id, first_approver_id, holiday_status_id,
            holiday_type, name, notes, number_of_days, second_approver_id,
            state, create_uid, create_date, write_uid, write_date, %s)
        SELECT category_id, date_from, date_to, department_id, employee_id,
            first_approver_id, holiday_status_id, holiday_type, name, notes,
            number_of_days, second_approver_id, state, create_uid,
            create_date, write_uid, write_date, id
        FROM hr_holidays
        WHERE %s = 'add'
        RETURNING id, %s
        """, (
            AsIs(openupgrade.get_legacy_name('holidays_id')),
            AsIs(openupgrade.get_legacy_name('type')),
            AsIs(openupgrade.get_legacy_name('holidays_id')),
        ),
    )
    new_rows = env.cr.fetchall()
    # fix parent_id:
    openupgrade.logged_query(
        env.cr, """
        UPDATE hr_leave_allocation hla1
        SET parent_id = hla2.id
        FROM hr_holidays hh1
        INNER JOIN hr_holidays hh2 ON hh1.parent_id = hh2.id
        INNER JOIN hr_leave_allocation hla2 ON hh2.id = hla2.%s
        WHERE hla1.%s = hh1.id
        """, (
            AsIs(openupgrade.get_legacy_name('holidays_id')),
            AsIs(openupgrade.get_legacy_name('holidays_id')),
        ),
    )
    # update many2ones of other models
    env.cr.execute("""
        SELECT model, name
        FROM ir_model_fields
        WHERE relation = 'hr_leave_allocation' AND ttype = 'many2one'
            AND model NOT IN ('hr.holidays', 'hr.leave.allocation')
    """)
    for field in env.cr.fetchall():
        for row in new_rows:
            table = field[0].replace('.', '_')
            env.cr.execute(
                """
                UPDATE %s
                SET %s = %s
                WHERE %s = %s
                """ % (table, field[1], field[1], row[0], row[1])
            )
    # update mail_message
    openupgrade.logged_query(
        env.cr, """
        UPDATE mail_message mm
        SET model = 'hr.leave.allocation', res_id = hla.id
        FROM hr_leave_allocation hla
        WHERE mm.res_id = hla.%s AND mm.model = 'hr.holidays'
        """, (
            AsIs(openupgrade.get_legacy_name('holidays_id')),
        ),
    )
    # update mail_followers
    openupgrade.logged_query(
        env.cr, """
        UPDATE mail_followers mf
        SET res_model = 'hr.leave.allocation', res_id = hla.id
        FROM hr_leave_allocation hla
        WHERE mf.res_id = hla.%s AND mf.res_model = 'hr.holidays'
        """, (
            AsIs(openupgrade.get_legacy_name('holidays_id')),
        ),
    )
    # update attachments
    openupgrade.logged_query(
        env.cr, """
        UPDATE ir_attachment ia
        SET res_model = 'hr.leave.allocation', res_id = ia.id
        FROM hr_leave_allocation hla
        WHERE ia.res_id = hla.%s AND ia.res_model = 'hr.holidays'
        """, (
            AsIs(openupgrade.get_legacy_name('holidays_id')),
        ),
    )


def delete_hr_holidays_model(cr):
    """Delete old hr.holidays model."""
    openupgrade.logged_query(
        cr,
        "DELETE FROM ir_model WHERE model = %s",
        ('hr.holidays', )
    )
    openupgrade.logged_query(
        cr,
        "DELETE FROM ir_model_data WHERE model = %s",
        ('hr.holidays', )
    )


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    fill_hr_holidays_dates(cr)
    fill_hr_leave_type_validation_type(cr)
    fill_hr_leave_type_allocation_type(cr)
    fill_hr_leave(env)
    fill_hr_leave_request_dates(cr)
    fill_hr_leave_allocation(env)
    openupgrade.load_data(
        cr, 'hr_holidays', 'migrations/12.0.1.5/noupdate_changes.xml')
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
    delete_hr_holidays_model(cr)
