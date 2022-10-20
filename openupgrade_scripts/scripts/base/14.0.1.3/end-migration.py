# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def uninstall_conflicting_it_edi(cr):
    it_edi_conflicting_modules = ("l10n_it_edi", "l10n_it_fatturapa")
    if all(
        openupgrade.is_module_installed(cr.cr, m) for m in it_edi_conflicting_modules
    ):
        it_edi_module = cr["ir.module.module"].search(
            [
                ("name", "=", "l10n_it_edi"),
            ],
            limit=1,
        )
        it_edi_module.button_uninstall()


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
    uninstall_conflicting_it_edi(env)
