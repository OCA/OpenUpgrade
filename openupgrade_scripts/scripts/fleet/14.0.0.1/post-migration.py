# Copyright (C) 2021 Open Source Integrators <https://www.opensourceintegrators.com>
# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def fill_fleet_vehicle_log_contract_fields(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE
            fleet_vehicle_log_contract as fvlc
        SET
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


def fill_fleet_vehicle_log_services_fields(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE
            fleet_vehicle_log_services as fvls
        SET
            vehicle_id = fvc.vehicle_id,
            amount = fvc.amount,
            company_id = fvc.company_id,
            odometer_id = fvc.odometer_id,
            description = fvc.description,
            date = fvc.date,
            service_type_id = fvc.cost_subtype_id
        FROM
            fleet_vehicle_cost as fvc
        WHERE
            fvc.id =  fvls.cost_id
        """,
    )


def fill_fleet_vehicle_log_contract_service_ids(env):
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO fleet_service_type_fleet_vehicle_log_contract_rel
        (fleet_vehicle_log_contract_id, fleet_service_type_id)
        SELECT fvlc.id, fvc.cost_subtype_id
        FROM fleet_vehicle_log_contract fvlc
        JOIN fleet_vehicle_cost fvc ON fvc.parent_id = fvlc.cost_id
        WHERE fvc.cost_subtype_id IS NOT NULL
        """,
    )


def set_fleet_vehicle_log_services_state(env):
    """Set all records to 'done', as it was the supposed option in v13 and the ORM
    default 'todo' is not suitable.
    """
    openupgrade.logged_query(
        env.cr, "UPDATE fleet_vehicle_log_services SET state = 'done'"
    )


def map_fleet_vehicle_log_contract_state(env):
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("state"),
        "state",
        [("diesoon", "open")],
        table="fleet_vehicle_log_contract",
    )


def delete_domain_from_view(env):
    view = env.ref("fleet.fleet_vehicle_service_types_action")
    view.domain = False


def recompute_fleet_vehicle_log_contract_name(env):
    contracts = (
        env["fleet.vehicle.log.contract"].with_context(active_test=False).search([])
    )
    contracts._compute_contract_name()


@openupgrade.migrate()
def migrate(env, version):
    fill_fleet_vehicle_log_contract_fields(env)
    fill_fleet_vehicle_log_services_fields(env)
    fill_fleet_vehicle_log_contract_service_ids(env)
    set_fleet_vehicle_log_services_state(env)
    map_fleet_vehicle_log_contract_state(env)
    delete_domain_from_view(env)
    openupgrade.load_data(env.cr, "fleet", "14.0.0.1/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "fleet.fleet_rule_cost_visibility_manager",
            "fleet.fleet_rule_cost_visibility_user",
            "fleet.fleet_rule_fuel_log_visibility_manager",
            "fleet.fleet_rule_fuel_log_visibility_user",
            "fleet.ir_rule_fleet_cost",
            "fleet.ir_rule_fleet_log_fuel",
        ],
    )
    recompute_fleet_vehicle_log_contract_name(env)
