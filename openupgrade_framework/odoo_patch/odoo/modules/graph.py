# Copyright Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import odoo
from odoo.modules.graph import Graph


def update_from_db(self, cr):
    """ Prevent reloading of demo data from the new version on major upgrade """
    Graph.update_from_db._original_method(self, cr)
    if (
        "base" in self
        and self["base"].dbdemo
        and self["base"].installed_version < odoo.release.major_version
    ):
        cr.execute("UPDATE ir_module_module SET demo = false")
        for package in self.values():
            package.dbdemo = False


update_from_db._original_method = Graph.update_from_db
Graph.update_from_db = update_from_db
