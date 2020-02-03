# -*- coding: utf-8 -*-
# Copyright 2016 Tecnativa - Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from openerp.modules.registry import RegistryManager


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    pool = RegistryManager.get(env.cr.dbname)
    openupgrade.set_defaults(
        env.cr, pool, {'website': [('cdn_filters', None)]}, use_orm=True,
    )
    openupgrade.load_data(
        env.cr, 'website', 'migrations/9.0.1.0/noupdate_changes.xml',
    )
    # Remove action from main website backend menu
    env.ref("website.menu_website_configuration").action = False
