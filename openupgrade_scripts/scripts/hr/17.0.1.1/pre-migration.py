# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# Copyright 2025 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _rename_subscription_department_ids_m2m(env):
    openupgrade.logged_query(
        env.cr,
        """ALTER TABLE hr_department_mail_channel_rel
        RENAME TO discuss_channel_hr_department_rel""",
    )
    openupgrade.logged_query(
        env.cr,
        """ALTER TABLE discuss_channel_hr_department_rel
        RENAME mail_channel_id TO discuss_channel_id""",
    )


def _fill_hr_contract_type_code(env):
    openupgrade.logged_query(
        env.cr, "ALTER TABLE hr_contract_type ADD COLUMN IF NOT EXISTS code VARCHAR"
    )
    openupgrade.logged_query(
        env.cr, "UPDATE hr_contract_type SET code = name WHERE code IS NULL"
    )


def _hr_plan_sync_to_mail_activity_plan(env):
    employee_model = env["ir.model"].search([("model", "=", "hr.employee")])
    # sync hr.plan to mail.activity.plan
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE mail_activity_plan ADD COLUMN IF NOT EXISTS department_id INTEGER,
        ADD COLUMN IF NOT EXISTS hr_plan_legacy_id INTEGER""",
    )
    hr_plan_query = f"""
        INSERT INTO mail_activity_plan (
            company_id, res_model_id, create_uid, write_uid, name, res_model,
            active, create_date, write_date, department_id, hr_plan_legacy_id
        )
        SELECT
            company_id, {employee_model.id}, create_uid, write_uid, name, 'hr.employee',
            active, create_date, write_date, department_id, id
        FROM hr_plan
        """
    openupgrade.logged_query(env.cr, hr_plan_query)
    # sync hr.plan.activitype.type to mail.activity.plan.template
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE mail_activity_plan_template
        ADD COLUMN hr_plan_activity_type_legacy_id INTEGER""",
    )
    hr_plan_activity_type_query = """
        INSERT INTO mail_activity_plan_template (
            activity_type_id, responsible_id, plan_id, responsible_type,
            summary, note, create_uid, write_uid, create_date,
            write_date, hr_plan_activity_type_legacy_id
        )
        SELECT
            hpat.activity_type_id, hpat.responsible_id, map.id, hpat.responsible,
            hpat.summary, hpat.note, hpat.create_uid, hpat.write_uid, hpat.create_date,
            hpat.write_date, hpat.id
        FROM hr_plan_activity_type hpat
        JOIN mail_activity_plan map ON hpat.plan_id = map.hr_plan_legacy_id
        """
    openupgrade.logged_query(env.cr, hr_plan_activity_type_query)
    # Reassign standard data XML-IDs for pointing to the new records
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_model_data imd
        SET model = 'mail.activity.plan', res_id = map.id
        FROM ir_model_data imd2
        JOIN mail_activity_plan map ON
            map.hr_plan_legacy_id = imd2.res_id
            AND imd2.name IN ('onboarding_plan', 'offboarding_plan')
            AND imd2.module = 'hr'
        WHERE imd.id = imd2.id""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_model_data imd
        SET model = 'mail.activity.plan.template', res_id = mapt.id
        FROM ir_model_data imd2
        JOIN mail_activity_plan_template mapt ON
            mapt.hr_plan_activity_type_legacy_id = imd2.res_id
            AND imd2.name IN (
                'onboarding_setup_it_materials',
                'onboarding_plan_training',
                'onboarding_training',
                'offboarding_setup_compute_out_delais',
                'offboarding_take_back_hr_materials'
            )
            AND imd2.module = 'hr'
        WHERE imd.id = imd2.id""",
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
    _rename_subscription_department_ids_m2m(env)
    _fill_hr_contract_type_code(env)
    _hr_plan_sync_to_mail_activity_plan(env)
    _hr_work_location_fill_location_type(env)
