# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def _migrate_website_multi(env):
    """If website_multi from odoo/odoo-extra is installed. In v9 now it's
    integrated on core 'website' module."""
    openupgrade.update_module_names(
        env.cr, [('website_multi', 'website')], merge_modules=True,
    )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    # Change noupdate flag for ir.ui.menu entry
    env.ref('website.menu_website').noupdate = False
    _migrate_website_multi(env)
