# Copyright (C) 2021 Open Source Integrators <https://www.opensourceintegrators.com/>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Load noupdate changes
    openupgrade.load_data(env.cr, "fleet", "14.0.0.1/noupdate_changes.xml")

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE
            fleet_vehicle_log_contract as fvlc set
            vehicle_id = fvc.vehicle_id,
            amount = fvc.amount,
            cost_subtype_id = fvc.cost_subtype_id,
            company_id = fvc.company_id,
            date = fvc.date
        FROM
            fleet_vehicle_cost as fvc
        WHERE
            fvc.id =  fvlc.cost_id
        """,
    )

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE
            fleet_vehicle_log_services as fvls set
            vehicle_id = fvc.vehicle_id,
            amount = fvc.amount,
            company_id = fvc.company_id,
            odometer_id = fvc.odometer_id,
            description = fvc.description,
            date = fvc.date
        FROM
            fleet_vehicle_cost as fvc
        WHERE
            fvc.id =  fvls.cost_id
        """,
    )

    openupgrade.logged_query(
        env.cr,
        """
        DELETE
            from ir_model
        where id=(select res_id from ir_model_data
        where model='ir.model' and name='model_fleet_vehicle_cost'
        )""",
    )
