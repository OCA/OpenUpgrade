# -*- coding: utf-8 -*-
# Copyright 2018 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def update_resource_resource_time_efficiency(cr):
    """The time_efficiency now is in percent instead of unity values."""
    cr.execute(
        """
        UPDATE resource_resource
        SET time_efficiency = COALESCE(time_efficiency, 0) * 100
        """
    )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    update_resource_resource_time_efficiency(cr)
