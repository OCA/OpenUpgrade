# Copyright Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import os

import odoo
from odoo.modules.module_graph import ModuleGraph


def _update_from_database(self, *args, **kwargs) -> None:
    """Prevent reloading of demo data from the new version on major upgrade"""
    ModuleGraph._update_from_database._original_method(self, *args, **kwargs)

    if os.environ.get("OPENUPGRADE_USE_DEMO", "") == "yes":
        return
    if (
        "base" in self._modules
        and self._modules["base"].demo
        and self._modules["base"].installed_version < odoo.release.major_version
    ):
        self._cr.execute("UPDATE ir_module_module SET demo = false")
        for module in self._modules.values():
            module.demo = False


_update_from_database._original_method = ModuleGraph._update_from_database
ModuleGraph._update_from_database = _update_from_database
