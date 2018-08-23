# -*- coding: utf-8 -*-
# © 2018 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):

    openupgrade.load_data(
        env.cr, 'procurement', 'migrations/9.0.1.0/noupdate_changes.xml',
    )
