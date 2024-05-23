# Copyright Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import os

import odoo
from odoo.modules.graph import Graph


def update_from_db(self, cr):
    """Prevent reloading of demo data from the new version on major upgrade"""
    Graph.update_from_db._original_method(self, cr)
    if os.environ.get("OPENUPGRADE_USE_DEMO", "") == "yes":
        return
    if (
        "base" in self
        and self["base"].dbdemo
        and self["base"].installed_version < odoo.release.major_version
    ):
        cr.execute("UPDATE ir_module_module SET demo = false")
        for package in self.values():
            package.dbdemo = False


def add_modules(self, cr, module_list, force=None):
    """Add extra dependencies directly to the graph for immediate installation and
    proper dependency resolution.
    """
    modules_in = list(module_list)
    dependencies = module_list
    while dependencies:
        cr.execute(
            """
            SELECT DISTINCT dep.name
            FROM
                ir_module_module,
                ir_module_module_dependency dep
            WHERE
                module_id = ir_module_module.id
                AND ir_module_module.name in %s
                AND dep.name not in %s
            """,
            (tuple(dependencies), tuple(module_list)),
        )
        dependencies = [x[0] for x in cr.fetchall()]
        module_list += dependencies
    # Set proper state for new dependencies so that any init scripts are run
    cr.execute(
        """
        UPDATE ir_module_module SET state = 'to install'
        WHERE name IN %s AND name NOT IN %s AND state = 'uninstalled'
        """,
        (tuple(module_list), tuple(modules_in)),
    )
    return Graph.add_modules._original_method(self, cr, module_list, force=force)


update_from_db._original_method = Graph.update_from_db
Graph.update_from_db = update_from_db
add_modules._original_method = Graph.add_modules
Graph.add_modules = add_modules
