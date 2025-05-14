# Copyright 2025 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.logging()
def _recompute_slide_slide_type(env):
    """Recompute the field by calling its compute method."""
    env["slide.slide"].search([])._compute_slide_type()


@openupgrade.migrate()
def migrate(env, version):
    _recompute_slide_slide_type(env)
