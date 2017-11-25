# -*- coding: utf-8 -*-
# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_xmlid_renames = [
    ('fleet.group_fleet_manager', 'fleet.fleet_group_manager'),
    ('fleet.group_fleet_user', 'fleet.fleet_group_user'),
    (
        'fleet.fleet_user_contract_visibility',
        'fleet.fleet_rule_contract_visibility_user'
    ),
    (
        'fleet.fleet_user_contract_visibility_manager',
        'fleet.fleet_rule_contract_visibility_manager'
    ),
    (
        'fleet.fleet_user_cost_visibility',
        'fleet.fleet_rule_cost_visibility_user'
    ),
    (
        'fleet.fleet_user_cost_visibility_manager',
        'fleet.fleet_rule_cost_visibility_manager'
    ),
    (
        'fleet.fleet_user_fuel_log_visibility',
        'fleet.fleet_rule_fuel_log_visibility_user'
    ),
    (
        'fleet.fleet_user_fuel_log_visibility_manager',
        'fleet.fleet_rule_fuel_log_visibility_manager'
    ),
    (
        'fleet.fleet_user_odometer_visibility',
        'fleet.fleet_rule_odometer_visibility_user'
    ),
    (
        'fleet.fleet_user_odometer_visibility_manager',
        'fleet.fleet_rule_odometer_visibility_manager'
    ),
    (
        'fleet.fleet_user_service_visibility',
        'fleet.fleet_rule_service_visibility_user'
    ),
    (
        'fleet.fleet_user_service_visibility_manager',
        'fleet.fleet_rule_service_visibility_manager'
    ),
    (
        'fleet.fleet_user_vehicle_visibility',
        'fleet.fleet_rule_vehicle_visibility_user'
    ),
    (
        'fleet.fleet_user_vehicle_visibility_manager',
        'fleet.fleet_rule_vehicle_visibility_manager'
    ),

]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
