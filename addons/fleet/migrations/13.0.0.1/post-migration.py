# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_fleet_vehicle_cost_company_id(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE fleet_vehicle_cost fvc
        SET company_id = fv.company_id
        FROM fleet_vehicle fv
        WHERE fvc.vehicle_id = fv.id
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_fleet_vehicle_cost_company_id(env.cr)
    openupgrade.load_data(env.cr, 'fleet', 'migrations/13.0.0.1/noupdate_changes.xml')
