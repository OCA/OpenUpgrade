# Copyright 2018 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_column_copies = {
    'mrp_repair_line': [
        ('price_unit', None, None),
    ],
    'mrp_repair_fee': [
        ('price_unit', None, None),
    ],
}

_column_renames = {
    'mrp_repair_line': [
        ('to_invoice', None),
    ],
    'mrp_repair_fee': [
        ('to_invoice', None),
    ],
}


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    openupgrade.copy_columns(cr, _column_copies)
    openupgrade.rename_columns(cr, _column_renames)
