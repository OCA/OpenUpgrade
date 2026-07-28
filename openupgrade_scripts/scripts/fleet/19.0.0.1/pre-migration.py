# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def fleet_vehicle(env):
    """
    Handle new fields in fleet.vehicle:
    - create range_unit with default km
    - create co2_emission_unit and fill via SQL
    - rename first_contract_date to contract_date_start
    """
    openupgrade.add_columns(
        env,
        [
            (
                "fleet.vehicle",
                "range_unit",
                "selection",
                "km",
                "fleet_vehicle",
            ),
            (
                "fleet.vehicle",
                "co2_emission_unit",
                "selection",
                "g/km",
                "fleet_vehicle",
            ),
        ],
    )
    openupgrade.rename_fields(
        env,
        [
            (
                "fleet.vehicle",
                "fleet_vehicle",
                "first_contract_date",
                "contract_date_start",
            )
        ],
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE fleet_vehicle
        SET co2_emission_unit='g/mi'
        WHERE
        range_unit <> 'km'
        AND co2_emission_unit IS NULL
        """,
    )


def fleet_vehicle_log_services(env):
    """
    Add new stored related columns and fill with SQL
    """
    openupgrade.add_columns(
        env,
        [
            (
                "fleet.vehicle.log.services",
                "brand_id",
                "many2one",
                None,
                "fleet_vehicle_log_services",
            ),
            (
                "fleet.vehicle.log.services",
                "model_id",
                "many2one",
                None,
                "fleet_vehicle_log_services",
            ),
        ],
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE
            fleet_vehicle_log_services
        SET
            model_id=fleet_vehicle.model_id,
            brand_id=fleet_vehicle_model.brand_id
        FROM
            fleet_vehicle
        LEFT JOIN
            fleet_vehicle_model
            ON fleet_vehicle.model_id=fleet_vehicle_model.id
        WHERE
            vehicle_id=fleet_vehicle.id
        """,
    )


def fleet_vehicle_odometer(env):
    """
    Add and fill fleet.vehicle.odometer#driver_id column
    """
    openupgrade.add_columns(
        env,
        [
            (
                "fleet.vehicle.odometer",
                "driver_id",
                "many2one",
                None,
                "fleet_vehicle_odometer",
            ),
        ],
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE
            fleet_vehicle_odometer
        SET
            driver_id=fleet_vehicle.driver_id
        FROM
            fleet_vehicle
        WHERE
            fleet_vehicle_odometer.vehicle_id=fleet_vehicle.id
            AND fleet_vehicle_odometer.driver_id IS NULL
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    fleet_vehicle(env)
    fleet_vehicle_log_services(env)
    fleet_vehicle_odometer(env)
