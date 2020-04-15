# Copyright 2020 ForgeFlow <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_unlink_by_xmlid = [
    # stock.location
    'stock.location_inventory',
    'stock.location_production',
    'stock.stock_location_scrapped',
    # "stock.location_procurement", obsolete but don't delete it
    # because may be linked to old quants/moves
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(env, _unlink_by_xmlid)
