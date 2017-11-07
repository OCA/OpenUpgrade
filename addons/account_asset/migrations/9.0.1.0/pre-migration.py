# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


field_renames = [
    # renamings with oldname attribute - They also need the rest of operations
    ('account.asset.asset', 'account_asset_asset', 'purchase_date', 'date'),
    ('account.asset.asset', 'account_asset_asset', 'purchase_value', 'value'),
    ('account.asset.category', 'account_asset_category',
     'account_expense_depreciation_id', 'account_income_recognition_id'),
]


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.rename_fields(env, field_renames)
