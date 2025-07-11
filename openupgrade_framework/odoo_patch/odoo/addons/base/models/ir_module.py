# Copyright Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.base.models.ir_module import Module


def update_list(self):
    """
    Mark auto_install modules as to install if all their dependencies are some kind of
    installed.
    Ignore localization modules that are set to auto_install
    """
    result = Module.update_list._original_method(self)
    new_auto_install_modules = self.browse([])
    for module in self.env["ir.module.module"].search(
        [
            ("auto_install", "=", True),
            ("state", "=", "uninstalled"),
            ("name", "not like", ("l10n_%")),
        ]
    ):
        if all(
            state in ("to upgrade", "to install", "installed")
            for state in module.dependencies_id.mapped("state")
        ):
            new_auto_install_modules |= module
    if new_auto_install_modules:
        new_auto_install_modules.button_install()
    return result


update_list._original_method = Module.update_list
Module.update_list = update_list
