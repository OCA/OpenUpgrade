# Copyright 2023 Coop IT Easy (https://coopiteasy.be)
# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def create_work_contact(env):
    """Create work_contact_id for model hr.employee.base

    If the employee is linked to a res.user, we set the partner_id of the
    res.user as a work_contact_id.

    If the employee is not linked to a res.user. Then we try to match an
    existing partner with the same email address. If one is found, then
    we assign it as work_contact_id. If several are found, we raise a
    warning and we link the first one found. If none are found, then we
    create a new partner.
    """
    employees = env["hr.employee"].search([])

    for employee in employees:
        if employee.user_id and employee.user_id.partner_id:
            partner = employee.user_id.partner_id
            if (
                not employee.work_email
                and not employee.mobile_phone
                or (
                    employee.work_email == partner.email
                    and employee.mobile_phone == partner.mobile
                )
                or (not employee.work_email and employee.mobile_phone == partner.mobile)
                or (not employee.mobile_phone and employee.work_email == partner.email)
            ):
                employee.work_contact_id = partner
                _logger.info(
                    "Set work_contact_id of hr.employee(%s) to "
                    "res.partner(%s) (the res.user partner).",
                    employee.id,
                    partner.id,
                )
        else:
            matching_partner = env["res.partner"].search(
                [
                    ("email", "=", employee.work_email),
                    ("mobile", "=", employee.mobile_phone),
                ]
            )
            nb_matching_partner = len(matching_partner)
            if nb_matching_partner == 1:
                employee.work_contact_id = matching_partner
                _logger.info(
                    "Found res.partner(%s) that match hr.employee(%s). "
                    "work_contact_id is set accordingly.",
                    matching_partner.id,
                    employee.id,
                )
            elif nb_matching_partner > 1:
                partner = matching_partner[0]
                employee.work_contact_id = partner
                _logger.warning(
                    "Several res.partner found for hr.employee(%s): "
                    "res.partner(%s). "
                    "Arbitrarily, the res.partner(%s) (the first one) "
                    "is used for work_contact_id of the hr.employee(%s).",
                    employee.id,
                    ", ".join(str(v) for v in matching_partner.ids),
                    partner.id,
                    employee.id,
                )
            else:
                partner_vals = {
                    "name": employee.name,
                    "email": employee.work_email,
                    "mobile": employee.mobile_phone,
                    "company_id": employee.company_id.id,
                    "image_1920": employee.image_1920,
                }
                partner = env["res.partner"].create(partner_vals)
                employee.work_contact_id = partner
                _logger.info(
                    "No res.partner found for hr.employee(%s). "
                    "A new partner has been created and linked to "
                    "the employee: res.partner(%s).",
                    employee.id,
                    partner.id,
                )


def fill_master_department_id(cr):
    """Fill master_department_id based on parent_path"""
    openupgrade.logged_query(
        cr,
        """
        UPDATE hr_department
        SET master_department_id = split_part(parent_path, '/', 1)::int
        WHERE parent_path is not NULL;
        """,
    )


def _hr_plan_activity_type_m2m_to_o2m(env):
    """Before, the activities in plans (hr.plan) were linked to the
    plan_activity_type_ids field with a m2m field, now the field
    is an o2m. We define the data in the table hr_plan_activity_type according to the
    table ou_legacy_16_0_hr_plan_hr_plan_activity_type_rel that we have defined
    previously in pre-migration to ensure that no data is lost.
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_plan_activity_type hpat
        SET plan_id = rel.hr_plan_id
        FROM ou_legacy_16_0_hr_plan_hr_plan_activity_type_rel rel
        WHERE rel.hr_plan_activity_type_id = hpat.id
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO hr_plan_activity_type (
            plan_id,
            activity_type_id,
            summary,
            responsible,
            responsible_id,
            note,
            create_uid,
            create_date,
            write_uid,
            write_date
        )
        SELECT rel.hr_plan_id,
            detail.activity_type_id,
            detail.summary,
            detail.responsible,
            detail.responsible_id,
            detail.note,
            detail.create_uid,
            detail.create_date,
            detail.write_uid,
            detail.write_date
        FROM ou_legacy_16_0_hr_plan_hr_plan_activity_type_rel rel
        JOIN hr_plan_activity_type detail ON rel.hr_plan_activity_type_id = detail.id
        WHERE detail.plan_id != rel.hr_plan_id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _hr_plan_activity_type_m2m_to_o2m(env)
    fill_master_department_id(env.cr)
    create_work_contact(env)
    openupgrade.load_data(env.cr, "hr", "16.0.1.1/noupdate_changes.xml")
