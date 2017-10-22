# -*- coding: utf-8 -*-
# © 2017 Paul Catinean <https://www.pledra.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def migrate_bom(env):
    # Set default values from field definition as this is a new field and
    # the default val resembles the previous behavior best
    default_specs = {
        'mrp.bom': [('ready_to_produce', None)]
    }
    openupgrade.set_defaults(env.cr, env.pool, default_specs=default_specs)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    migrate_bom(env)
