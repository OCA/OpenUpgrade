# -*- coding: utf-8 -*-
# Copyright 2018 Vicent Cubells - Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def update_use_pad(cr):
    """
    Update use_pad in all projects
    """
    cr.execute("""
        UPDATE project_project SET use_pads = True;
    """)


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    update_use_pad(cr)
