# -*- coding: utf-8 -*-
# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

COLUMN_COPIES = {
    'rating_rating': [
        ('res_model', None, None),
    ],
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, COLUMN_COPIES)
