# Copyright Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.modules.migration import MigrationManager


def migrate_module(self, pkg, stage):
    """In openupgrade, also run migration scripts upon installation.
    We want to always pass in pre and post migration files and use a new
    argument in the migrate decorator (explained in the docstring)
    to decide if we want to do something if a new module is installed
    during the migration.
    We trick Odoo into running the scripts by temporarily changing the module
    state.
    """
    to_install = pkg.state == "to install"
    if to_install:
        pkg.state = "to upgrade"
    MigrationManager.migrate_module._original_method(self, pkg, stage)
    if to_install:
        pkg.state = "to install"


migrate_module._original_method = MigrationManager.migrate_module
MigrationManager.migrate_module = migrate_module
