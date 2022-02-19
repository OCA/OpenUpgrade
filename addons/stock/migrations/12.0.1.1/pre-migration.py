# Copyright 2019 Eficent <http://www.eficent.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_column_copies = {
    'procurement_rule': [
        ('action', None, None),
    ],
}

_column_renames = {
    'stock_move':
    [
        ('push_rule_id', None),
    ],
}

_model_renames = [
    ('procurement.rule', 'stock.rule'),
]

_table_renames = [
    ('procurement_rule', 'stock_rule'),
]


def switch_stock_xml_id_noupdate(cr):
    """Main warehouse references records have an associated XML-ID, that was
    updated in v11 through a method and maintain as XML noupdate=0 data, so
    they weren't removed on updates, but now on v12, that XML-IDs are
    noupdate=1, and no XML data in provided, so on regular update process, they
    are tried to be removed. We switch them to noupdate=1 for avoiding this
    problem.
    """
    openupgrade.logged_query(
        cr, """
        UPDATE ir_model_data
        SET noupdate = True
        WHERE module = 'stock'
        AND name IN %s""", ((
            'stock_location_stock',
            'stock_location_company',
            'stock_location_output',
            'location_pack_zone',
            'picking_type_internal',
            'picking_type_in',
            'picking_type_out',
        ), ),
    )


def lift_fk_constrains_deleted_many2ones(cr):
    # deleted fields
    openupgrade.lift_constraints(cr, "barcode_nomenclature", "barcode_nomenclature_id")
    openupgrade.lift_constraints(cr, "stock_warehouse", "default_resupply_wh_id")


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    openupgrade.copy_columns(cr, _column_copies)
    openupgrade.rename_columns(cr, _column_renames)
    openupgrade.rename_models(cr, _model_renames)
    openupgrade.rename_tables(cr, _table_renames)
    switch_stock_xml_id_noupdate(cr)
    lift_fk_constrains_deleted_many2ones(cr)
    cr.execute(
        """
        ALTER TABLE stock_rule
        ADD COLUMN {} integer;
        """.format(openupgrade.get_legacy_name('loc_path_id'))
    )
    if openupgrade.table_exists(cr, 'stock_product_putaway_strategy'):
        cr.execute(
            """
            ALTER TABLE stock_fixed_putaway_strat
            ADD COLUMN {} integer;
            """.format(openupgrade.get_legacy_name('old_strat_id'))
        )
