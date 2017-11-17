# -*- coding: utf-8 -*-
# Copyright 2017 Bloopark <http://bloopark.de>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate(use_env=False)
def migrate(env, version):

    openupgrade.load_data(
        env.cd, 'payment', 'migrations/11.0.1.0/noupdate_changes.xml',
    )