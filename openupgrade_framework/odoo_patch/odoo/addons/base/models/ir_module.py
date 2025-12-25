# Copyright Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api

from odoo.addons.base.models.ir_module import IrModuleModule


@api.model
def update_list(self):
    """
    Mark auto_install modules as to install if all their dependencies are some kind of
    installed.
    Ignore localization modules that are set to auto_install
    """
    result = IrModuleModule.update_list._original_method(self)
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


def check_external_dependencies(self, module_name, newstate="to install"):
    try:
        IrModuleModule.check_external_dependencies._original_method(
            self, module_name, newstate=newstate
        )
    except AttributeError:  # pylint: disable=except-pass
        # this happens when a module is installed that doesn't exist in the new version
        pass


update_list._original_method = IrModuleModule.update_list
IrModuleModule.update_list = update_list
check_external_dependencies._original_method = (
    IrModuleModule.check_external_dependencies
)
IrModuleModule.check_external_dependencies = check_external_dependencies
