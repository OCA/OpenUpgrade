# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


_xmlid_renames = [
    ('base.menu_config', 'base_setup.menu_config'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
