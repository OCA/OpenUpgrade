# Copyright (C) 2022 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def recompute_duration_display(env):
    # We need to recomupte it once all has been migrated
    env["hr.leave"].search([])._compute_duration_display()


@openupgrade.migrate()
def migrate(env, version):
    recompute_duration_display(env)
