# Copyright Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import inspect

import odoo.modules.loading


def load_openerp_module(module_name):
    """
    Run pre-migration scripts of addons being installed
    """
    frame = inspect.currentframe()
    while frame.f_back:
        frame = frame.f_back
        f_locals = frame.f_locals

        expected_locals = (
            "new_install",
            "needs_update",
            "package",
            "migrations",
            "env",
        )
        if all(expected_local in f_locals for expected_local in expected_locals):
            if f_locals["needs_update"] and f_locals["new_install"]:
                f_locals["migrations"].migrate_module(f_locals["package"], "pre")
                f_locals["env"].flush_all()

    odoo.modules.loading.load_openerp_module._original_method(module_name)


load_openerp_module._original_method = odoo.modules.loading.load_openerp_module
odoo.modules.loading.load_openerp_module = load_openerp_module
