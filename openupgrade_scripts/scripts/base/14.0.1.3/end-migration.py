# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """Call disable_invalid_filters in every edition of openupgrade"""
    openupgrade.disable_invalid_filters(env)
    # web_diagram has been remove in V14
    # we merge into web, if no diagram are present, to avoid to
    # have to uninstall the module manually
    if not env["ir.ui.view"].search([("type", "=", "diagram")]):
        openupgrade.update_module_names(
            env.cr, [("web_diagram", "web")], merge_modules=True
        )
