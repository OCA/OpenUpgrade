# Copyright Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.modules.migration import MigrationManager


def _get_files(self):
    """Turns out Odoo SA sometimes add migration scripts that interfere with
    OpenUpgrade. Those we filter out here"""
    MigrationManager._get_files._original_method(self)
    to_exclude = [("analytic", "1.2")]
    for addon, version in to_exclude:
        self.migrations.get(addon, {}).get("module", {}).pop(version, None)
    for pkg in self.graph:
        if pkg.load_version or pkg.name not in self.migrations:
            continue
        # No version in the database means no data to migrate, and an empty
        # installed_version matches every version folder. Keep only the
        # OpenUpgrade scripts from upgrade_path.
        self.migrations[pkg.name]["module"] = {}
        self.migrations[pkg.name]["module_upgrades"] = {}


_get_files._original_method = MigrationManager._get_files
MigrationManager._get_files = _get_files
