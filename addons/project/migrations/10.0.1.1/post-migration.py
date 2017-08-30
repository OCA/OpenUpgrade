# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """UPDATE project_project
        SET active=False
        WHERE state IN ('cancelled', 'close')"""
    )
    openupgrade.load_data(
        env.cr, 'project', 'migrations/10.0.1.1/noupdate_changes.xml',
    )
