# Copyright 2025 L4 TECH S.L. (https://www.level4.es)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def fill_fleet_vehicle_log_services_x_account_move_line_id(env):
    vendor_bill_service = env.ref("account_fleet.data_fleet_service_type_vendor_bill")
    openupgrade.logged_query(
        env.cr,
        f"""
            UPDATE fleet_vehicle_log_services fvls
            SET account_move_line_id = aml.id
            FROM account_move am
            JOIN account_move_line aml ON aml.move_id = am.id
            WHERE fvls.vehicle_id = aml.vehicle_id
                AND fvls.description = aml.name
                AND fvls.vendor_id = aml.partner_id
                AND fvls.service_type_id = {vendor_bill_service.id}
                AND am.move_type = 'in_invoice' AND aml.display_type = 'product'
            """,
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_fleet_vehicle_log_services_x_account_move_line_id(env)
