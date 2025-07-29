# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    ICP = env["ir.config_parameter"]
    web_pwa_oca_installed = ICP.get_param("pwa.manifest.name")
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
        # Deduce whether it is necessary to install web_pwa_customize based on the
        # values previously defined in web_pwa_oca and the values that web will now use.
        short_name = ICP.get_param("pwa.manifest.short_name")
        background_color = ICP.get_param("pwa.manifest.background_color")
        theme_color = ICP.get_param("pwa.manifest.theme_color")
        if short_name or background_color != "#714B67" or theme_color != "#714B67":
            openupgrade.logged_query(
                env.cr,
                """
                UPDATE ir_module_module
                SET state = 'to install'
                WHERE name = 'web_pwa_customize'
                """,
            )
