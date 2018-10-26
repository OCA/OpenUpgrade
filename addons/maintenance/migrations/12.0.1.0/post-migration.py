# Copyright 2019 Eficent <http://www.eficent.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def empty_company_id_fields(cr):
    openupgrade.logged_query(
        cr, """
            UPDATE maintenance_equipment
            SET company_id = NULL
            """
    )
    openupgrade.logged_query(
        cr, """
            UPDATE maintenance_equipment_category
            SET company_id = NULL
            """
    )
    openupgrade.logged_query(
        cr, """
            UPDATE maintenance_request
            SET company_id = NULL
            """
    )
    openupgrade.logged_query(
        cr, """
            UPDATE maintenance_team
            SET company_id = NULL
            """
    )


def fill_maintenance_equipment_effective_date(cr):
    openupgrade.logged_query(
        cr, """
            UPDATE maintenance_equipment
            SET effective_date = create_date
            """
    )


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    empty_company_id_fields(cr)
    fill_maintenance_equipment_effective_date(cr)
