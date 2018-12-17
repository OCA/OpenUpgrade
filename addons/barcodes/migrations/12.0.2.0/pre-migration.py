# Copyright 2018 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    if not openupgrade.column_exists(cr, 'res_company', 'nomenclature_id'):
        openupgrade.add_fields(
            env, [
                ('nomenclature_id', 'res.company', 'res_company', 'many2one',
                 'int4', 'barcodes'),
            ],
        )

        # done here instead of post-migration to avoid the post-init-hook
        if openupgrade.table_exists(cr, 'stock_picking_type'):
            cr.execute(
                """
                UPDATE res_company rc
                SET nomenclature_id = spt.barcode_nomenclature_id
                FROM stock_picking_type spt
                LEFT JOIN stock_warehouse sw ON spt.warehouse_id = sw.id
                WHERE sw.company_id = rc.id
                    AND spt.barcode_nomenclature_id IS NOT NULL
                """
            )
