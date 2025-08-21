# Copyright 2025 Open Net Sàrl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def _set_power_unit(env):
    # if horspower is defined, set power_unit to horsepower
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE fleet_vehicle_model
        SET power_unit='horsepower'
        WHERE COALESCE(horsepower,0) > 0 AND COALESCE(power,0) = 0
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE fleet_vehicle
        SET power_unit='horsepower'
        WHERE COALESCE(horsepower,0) > 0 AND COALESCE(power,0) = 0
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _set_power_unit(env)
    data = env["ir.model.data"].search(
        [
            ("module", "=", "fleet"),
            (
                "name",
                "in",
                [
                    "model_a1",
                    "model_a3",
                    "model_a4",
                    "model_a5",
                    "model_a6",
                    "model_a7",
                    "model_a8",
                    "model_agila",
                    "model_ampera",
                    "model_antara",
                    "model_astra",
                    "model_astragtc",
                    "model_classa",
                    "model_classb",
                    "model_classc",
                    "model_classcl",
                    "model_classcls",
                    "model_classe",
                    "model_classgl",
                    "model_classglk",
                    "model_classm",
                    "model_classr",
                    "model_classs",
                    "model_classslk",
                    "model_classsls",
                    "model_combotour",
                    "model_corsa",
                    "model_insignia",
                    "model_meriva",
                    "model_mokka",
                    "model_q3",
                    "model_q5",
                    "model_q7",
                    "model_serie1",
                    "model_serie3",
                    "model_serie5",
                    "model_serie6",
                    "model_serie7",
                    "model_seriehybrid",
                    "model_seriem",
                    "model_seriex",
                    "model_seriez4",
                    "model_tt",
                    "model_zafira",
                    "model_zafiratourer",
                ],
            ),
        ]
    )
    data.unlink()
