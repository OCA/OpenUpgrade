# coding: utf-8
# © 2016 Opener B.V. - Stefan Rijnhart
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_tables(
        cr, [('sale_order_category_rel', 'sale_order_tag_rel')])
    openupgrade.rename_columns(cr, {
        'sale_order_tag_rel': [('category_id', 'tag_id')],
        'sale_order': [
            ('campaign_id', None),
            ('medium_id', None),
            ('source_id', None),
        ]})
