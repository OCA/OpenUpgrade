# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_unlink_by_xmlid = [
    # account.journal
    'point_of_sale.pos_sale_journal',
    # ir.sequence
    'point_of_sale.seq_picking_type_posout',
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(env, _unlink_by_xmlid)
    openupgrade.load_data(env.cr, 'point_of_sale', 'migrations/13.0.1.0.1/noupdate_changes.xml')
