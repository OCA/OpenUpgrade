# Copyright 2018-21 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    # pre-creation for speed up
    if not openupgrade.column_exists(cr, 'res_company', 'nomenclature_id'):
        openupgrade.add_fields(
            env, [
                ('nomenclature_id', 'res.company', 'res_company', 'many2one',
                 'int4', 'barcodes'),
            ],
        )

        # done here instead of post-migration to avoid the default
        if openupgrade.table_exists(cr, 'stock_picking_type'):
            openupgrade.logged_query(
                cr, """
                UPDATE res_company rc
                SET nomenclature_id = spt.barcode_nomenclature_id
                FROM stock_picking_type spt
                LEFT JOIN stock_warehouse sw ON spt.warehouse_id = sw.id
                WHERE sw.company_id = rc.id
                    AND spt.barcode_nomenclature_id IS NOT NULL"""
            )

        default_nomenclature_id = env["ir.model.data"].xmlid_to_res_id(
            "barcodes.default_barcode_nomenclature",
            raise_if_not_found=False,
        )
        if default_nomenclature_id:
            openupgrade.logged_query(
                env.cr, """
                UPDATE res_company
                SET nomenclature_id = {def_n_id}
                WHERE nomenclature_id IS NULL
                """.format(def_n_id=default_nomenclature_id)
            )
