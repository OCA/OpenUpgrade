# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_xmlid_renames = [
    # fleet.vehicle.model.brand
    ('fleet.brand_corre la licorne', 'fleet.brand_corre_la_licorne'),
    ('fleet.brand_land rover', 'fleet.brand_land_rover'),
    ('fleet.brand_tesla motors', 'fleet.brand_tesla_motors'),
    # ir.actions.act_window
    ('l10n_be_hr_payroll_fleet.fleet_config_settings_action', 'fleet.fleet_config_settings_action'),
    # ir.ui.menu
    ('l10n_be_hr_payroll_fleet.fleet_config_settings_action', 'fleet.fleet_config_settings_action'),
]

_field_renames = [
    ('fleet.vehicle.model.brand', 'fleet_vehicle_model_brand', 'image_medium', 'image_128'),
]

_field_adds = [
    ("manager_id", "fleet.vehicle.model", "fleet_vehicle_model", "many2one", False, "fleet"),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.add_fields(env, _field_adds)
    # Fix image of fleet.vehicle.model.brand after renaming column to image_128
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_attachment
        SET res_field = 'image_128'
        WHERE res_field = 'image_medium' and res_model = 'fleet.vehicle.model.brand'
        """,
    )
