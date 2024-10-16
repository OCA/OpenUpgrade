# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

_xmlids_renames = [
    (
        "hr.offboarding_plan",
        "hr.openupgrade_legacy_17_0_offboarding_plan",
    ),
    (
        "hr.onboarding_plan",
        "hr.openupgrade_legacy_17_0_onboarding_plan",
    ),
    (
        "hr.offboarding_setup_compute_out_delais",
        "hr.openupgrade_legacy_17_0_offboarding_setup_compute_out_delais",
    ),
    (
        "hr.offboarding_take_back_hr_materials",
        "hr.openupgrade_legacy_17_0_offboarding_take_back_hr_materials",
    ),
    (
        "hr.onboarding_plan_training",
        "hr.openupgrade_legacy_17_0_onboarding_plan_training",
    ),
    (
        "hr.onboarding_setup_it_materials",
        "hr.openupgrade_legacy_17_0_onboarding_setup_it_materials",
    ),
    (
        "hr.onboarding_training",
        "hr.openupgrade_legacy_17_0_onboarding_training",
    ),
]


def _hr_plan_sync_to_mail_activity_plan(env):
    employee_model = env["ir.model"].search([("model", "=", "hr.employee")])
    # Because when loading noupdate, we might create some duplicate plan data
    # Therefore check if those plan data still exist then skip insert
    env.cr.execute(
        """
        SELECT res_id FROM ir_model_data
        WHERE model='hr.plan' AND
        name in ('offboarding_plan', 'onboarding_plan')
        """
    )
    hr_plan_ids = tuple([d[0] for d in env.cr.fetchall()])

    # sync hr.plan to mail.activity.plan
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE mail_activity_plan ADD COLUMN IF NOT EXISTS department_id INTEGER,
        ADD COLUMN IF NOT EXISTS hr_plan_legacy_id INTEGER;
        """,
    )
    hr_plan_query = f"""
        INSERT INTO mail_activity_plan (company_id, res_model_id, create_uid,
        write_uid, name, res_model, active, create_date, write_date, department_id,
        hr_plan_legacy_id
        )
        SELECT company_id, {employee_model.id}, create_uid, write_uid, name,
        '{employee_model.model}', active, create_date, write_date, department_id, id
        FROM hr_plan t
    """
    if hr_plan_ids:
        hr_plan_query += f" WHERE t.id NOT IN {hr_plan_ids}"
    openupgrade.logged_query(
        env.cr,
        hr_plan_query,
    )

    # sync hr.plan.activitype.type to mail.activity.plan.template
    hr_plan_activity_type_query = """
        INSERT INTO mail_activity_plan_template (activity_type_id, responsible_id,
        plan_id, responsible_type, summary, note, create_uid, write_uid, create_date,
        write_date
        )
        SELECT activity_type_id, responsible_id, t2.id plan_id, responsible, summary,
        note, t1.create_uid, t1.write_uid, t1.create_date, t1.write_date
        FROM hr_plan_activity_type t1, mail_activity_plan t2
        WHERE t1.plan_id = t2.hr_plan_legacy_id
    """
    if hr_plan_ids:
        hr_plan_activity_type_query += f" AND t1.plan_id NOT IN {hr_plan_ids}"
    openupgrade.logged_query(
        env.cr,
        hr_plan_activity_type_query,
    )
    # Drop hr_plan_legacy_id column
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE mail_activity_plan DROP COLUMN hr_plan_legacy_id;
        """,
    )


def _employee_sync_address_home_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE hr_employee
            ADD COLUMN IF NOT EXISTS lang VARCHAR,
            ADD COLUMN IF NOT EXISTS private_city VARCHAR,
            ADD COLUMN IF NOT EXISTS private_country_id INTEGER,
            ADD COLUMN IF NOT EXISTS private_email VARCHAR,
            ADD COLUMN IF NOT EXISTS private_phone VARCHAR,
            ADD COLUMN IF NOT EXISTS private_state_id INTEGER,
            ADD COLUMN IF NOT EXISTS private_street VARCHAR,
            ADD COLUMN IF NOT EXISTS private_street2 VARCHAR,
            ADD COLUMN IF NOT EXISTS private_zip VARCHAR;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_employee t1
        SET lang = t2.lang,
            private_city = t2.city,
            private_country_id = t2.country_id,
            private_email = t2.email,
            private_phone = t2.phone,
            private_state_id = t2.state_id,
            private_street = t2.street,
            private_street2 = t2.street2,
            private_zip = t2.zip
        FROM res_partner t2
        WHERE t1.address_home_id = t2.id
        """,
    )


def _hr_work_location_fill_location_type(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE hr_work_location ADD COLUMN IF NOT EXISTS location_type VARCHAR;
        UPDATE hr_work_location
        SET location_type = 'office'
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _hr_plan_sync_to_mail_activity_plan(env)
    openupgrade.rename_xmlids(env.cr, _xmlids_renames)
    _employee_sync_address_home_id(env)
    _hr_work_location_fill_location_type(env)
