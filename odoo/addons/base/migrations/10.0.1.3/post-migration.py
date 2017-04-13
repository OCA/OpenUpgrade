# coding: utf-8
# © 2017 Opener BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.load_data(
        env.cr, 'base', 'migrations/10.0.1.3/noupdate_changes.xml'
    )
