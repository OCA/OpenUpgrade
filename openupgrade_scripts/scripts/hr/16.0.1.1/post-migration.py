# Copyright 2023 Coop IT Easy (https://coopiteasy.be)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openupgradelib import openupgrade
from psycopg2.extensions import AsIs

_logger = logging.getLogger(__name__)


def warn_about_dataloss(cr, source_relation_table, relation_comodel_field):
    """Warn user about data loss when migrating data from many2many to
    many2one.

    :param source_relation_table: The many2many relation table
    of the model that will be on the 'one' side of the relation
    :param relation_comodel_field: The name of the column containing ids
    of the 'many' part of the new relation.
    """
    openupgrade.logged_query(
        cr,
        """
        SELECT DISTINCT %(relation_comodel_field)s
        FROM %(source_relation_table)s
        WHERE %(relation_comodel_field)s IN (
            SELECT %(relation_comodel_field)s
            FROM %(source_relation_table)s
            GROUP BY %(relation_comodel_field)s
            HAVING COUNT(*) > 1
        )
        """,
        {
            "source_relation_table": AsIs(source_relation_table),
            "relation_comodel_field": AsIs(relation_comodel_field),
        },
    )
    for res in cr.fetchall():
        _logger.error(
            "hr.plan.activity.type(%s,) is linked to several hr.plan. "
            "hr.plan.activity.type can only be linked to one hr.plan. "
            "Fix these data before migrating to avoid data loss.",
            res[0],
        )


def m2m_to_o2m(
    env,
    model,
    field,
    source_relation_table,
    relation_source_field,
    relation_comodel_field,
):
    """Transform many2many relations into one2many (with possible data
    loss).

    Use rename_tables() in your pre-migrate script to keep the many2many
    relation table and give them as 'source_relation_table' argument.
    And remove foreign keys constraints with remove_tables_fks().

    :param model: The target registery model
    :param field: The field that changes from m2m to o2m
    :param source_relation_table: The (renamed) many2many relation table
    :param relation_source_field: The column name of the 'model' id
    in the relation table
    :param relation_comodel_field: The column name of the comodel id in
    the relation table
    """
    columns = env[model]._fields.get(field)
    target_table = env[columns.comodel_name]._table
    target_field = columns.inverse_name
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE %(target_table)s AS target
        SET %(target_field)s=source.%(relation_source_field)s
        FROM %(source_relation_table)s AS source
        WHERE source.%(relation_comodel_field)s=target.id
        """,
        {
            "target_table": AsIs(target_table),
            "target_field": AsIs(target_field),
            "source_relation_table": AsIs(source_relation_table),
            "relation_source_field": AsIs(relation_source_field),
            "relation_comodel_field": AsIs(relation_comodel_field),
        },
    )


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


@openupgrade.migrate()
def migrate(env, version):
    warn_about_dataloss(
        env.cr,
        "ou_legacy_16_0_hr_plan_hr_plan_activity_type_rel",
        "hr_plan_activity_type_id",
    )
    m2m_to_o2m(
        env,
        "hr.plan",
        "plan_activity_type_ids",
        "ou_legacy_16_0_hr_plan_hr_plan_activity_type_rel",
        "hr_plan_id",
        "hr_plan_activity_type_id",
    )
    fill_master_department_id(env.cr)
    create_work_contact(env)
    openupgrade.load_data(env.cr, "hr", "16.0.1.1/noupdate_changes.xml")
