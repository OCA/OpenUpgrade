# Copyright 2019 Onestein (<https://www.onestein.eu>)
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def empty_fleet_vehicle_first_contract_date_field(cr):
    openupgrade.logged_query(
        cr, """
            UPDATE fleet_vehicle
            SET first_contract_date = NULL
            """
    )


def empty_fleet_vehicle_log_contract_user_id_field(cr):
    openupgrade.logged_query(
        cr, """
            UPDATE fleet_vehicle_log_contract
            SET user_id = NULL
            """
    )


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    empty_fleet_vehicle_first_contract_date_field(cr)
    empty_fleet_vehicle_log_contract_user_id_field(cr)
