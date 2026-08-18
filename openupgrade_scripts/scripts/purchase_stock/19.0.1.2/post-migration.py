# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.m2o_to_x2m(
        env.cr,
        env["purchase.order"],
        "purchase_order",
        "reference_ids",
        "group_id",
    )
    openupgrade.load_data(
        env,
        "purchase_stock",
        "19.0.1.2/noupdate_changes.xml",
        xml_transformation_filename="19.0.1.2/noupdate_changes-transformation.xml",
    )
