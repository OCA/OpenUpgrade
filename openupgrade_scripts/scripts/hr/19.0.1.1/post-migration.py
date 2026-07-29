# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

from odoo.tools.mail import html2plaintext, is_html_empty

_deleted_xmlids = []


def fill_hr_version(env):
    """
    Create a hr.version per hr.employee if not already created by a contract.
    If hr_contract was installed, amend data resulting from renaming hr.contract to
    hr.version
    """
    fields = (
        "active",
        "additional_note",
        "address_id",
        "children",
        "country_id",
        "company_id",
        "department_id",
        "departure_date",
        "departure_description",
        "departure_reason_id",
        "distance_home_work",
        "distance_home_work_unit",
        "employee_type",
        "sex",
        "identification_id",
        "is_flexible",
        "is_fully_flexible",
        "job_id",
        "job_title",
        "km_home_work",
        "marital",
        "name",
        "passport_id",
        "private_city",
        "private_country_id",
        "private_state_id",
        "private_street",
        "private_street2",
        "private_zip",
        "spouse_birthdate",
        "spouse_complete_name",
        "ssnid",
        "work_location_id",
    )
    link_column = openupgrade.get_legacy_name("contract_id")
    env.cr.execute(
        f"ALTER TABLE hr_version ADD COLUMN IF NOT EXISTS {link_column} int",
    )
    env.cr.execute(f"UPDATE hr_version SET {link_column}=id")
    env.cr.execute(
        f"""
        UPDATE hr_version
        SET
        {", ".join(f"{field}=hr_employee.{field}" for field in fields)}
        FROM hr_employee
        WHERE
        hr_version.employee_id=hr_employee.id
        """
    )
    env.cr.execute(
        f"""
        INSERT INTO hr_version
        (
            employee_id, date_version, contract_date_start,
            last_modified_uid, last_modified_date, hr_responsible_id,
            resource_calendar_id,
            {", ".join(fields)}
        )
        SELECT
            id, create_date, create_date,
            write_uid, write_date, {env.ref("base.user_admin").id},
            resource_calendar_id,
            {", ".join(fields)}
        FROM hr_employee
        WHERE id NOT IN (
            SELECT employee_id FROM hr_version
        )
        """
    )
    env.cr.execute(
        f"""
        UPDATE hr_version
        SET hr_responsible_id={env.ref("base.user_admin").id}
        WHERE hr_responsible_id IS NULL
        """
    )
    env["hr.employee"]._cron_update_current_version_id()


def hr_employee_bank_account_ids(env):
    """
    Fill hr.employee#bank_account_ids
    """
    openupgrade.m2o_to_x2m(
        env.cr, env["hr.employee"], "hr_employee", "bank_account_ids", "bank_account_id"
    )
    # Set salary distribution to avoid error on _compute_primary_bank_account_id
    env.cr.execute(
        """
        UPDATE hr_employee
        SET salary_distribution = json_build_object(
            bank_account_id::text,
            json_build_object(
                'amount', 100.0,
                'sequence', 1,
                'amount_is_percentage', true
            )
        )
        WHERE bank_account_id IS NOT NULL
        """
    )


def hr_employee_notes(env):
    """
    Append hr.employee#note and hr.contract#note to hr.version#additional_note
    """
    env.cr.execute(
        """
        UPDATE
        hr_version
        SET
        additional_note=
            COALESCE(hr_version.additional_note || '\n', '') ||
            hr_employee.notes
        FROM
        hr_employee
        WHERE
        hr_version.employee_id=hr_employee.id
        AND
        hr_employee.notes IS NOT NULL
        """
    )
    if openupgrade.column_exists(env.cr, "hr_version", "notes"):
        # this is hr.contract#note, which is html
        env.cr.execute(
            "SELECT id, additional_note, notes FROM hr_version WHERE notes IS NOT NULL"
        )
        for _id, additional_note, notes in env.cr.fetchall():
            if is_html_empty(notes):
                continue
            notes = html2plaintext(notes)
            additional_note = (additional_note + "\n") if additional_note else ""
            env.cr.execute(
                "UPDATE hr_version SET additional_note=%s WHERE id=%s",
                (
                    additional_note + notes,
                    _id,
                ),
            )


@openupgrade.migrate()
def migrate(env, version):
    fill_hr_version(env)
    hr_employee_notes(env)
    hr_employee_bank_account_ids(env)
    openupgrade.load_data(env, "hr", "19.0.1.1/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(env, _deleted_xmlids)
