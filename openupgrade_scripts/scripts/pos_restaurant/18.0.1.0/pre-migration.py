# Copyright 2025 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

field_renames = [
    ("pos.config", "pos_config", "self_ordering_takeaway", "takeaway"),
    ("pos.config", "pos_config", "self_ordering_alternative_fp_id", "takeaway_fp_id"),
    ("pos.order", "pos_order", "take_away", "takeaway"),
]


@openupgrade.migrate()
def migrate(env, version=None):
    openupgrade.rename_fields(env, field_renames)
