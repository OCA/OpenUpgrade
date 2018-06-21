# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.map_values(
        env.cr, openupgrade.get_legacy_name('category'), 'category',
        [('both', 'contract')], table='fleet_service_type',
    )
    # Update state of all the contracts
    env['fleet.vehicle.log.contract'].scheduler_manage_contract_expiration()
