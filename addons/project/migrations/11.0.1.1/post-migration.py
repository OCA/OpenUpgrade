# -*- coding: utf-8 -*-
# © 2017 bloopark systems (<http://bloopark.de>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def set_default_values(env):
    """ Update with default values for new required fields """

    to_update = {
        'project.task.type': [
            ('legend_blocked', None),
            ('legend_done', None),
            ('legend_normal', None)
        ]
    }

    openupgrade.set_defaults(env.cr, env, to_update)


@openupgrade.migrate()
def migrate(env, version):
    set_default_values(env)
