# Copyright 2019 Eficent <http://www.eficent.com>
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


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    openupgrade.copy_columns(cr, _column_copies)
    openupgrade.rename_columns(cr, _column_renames)
    openupgrade.rename_models(cr, _model_renames)
    openupgrade.rename_tables(cr, _table_renames)
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
            """.format(openupgrade.get_legacy_name('putaway_strategy_id'))
        )
