# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    web_pwa_oca_installed = env["ir.config_parameter"].get_param("pwa.manifest.name")
    if web_pwa_oca_installed:
        openupgrade.rename_fields(
            env,
            [
                (
                    "res.config.settings",
                    "res_config_settings",
                    "web_pwa_oca",
                    "web_app_name",
                ),
            ],
        )
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE ir_config_parameter
            SET key = 'web.web_app_name'
            WHERE key = 'pwa.manifest.name'
            """,
        )
