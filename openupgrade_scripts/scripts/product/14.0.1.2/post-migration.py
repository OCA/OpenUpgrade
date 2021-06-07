# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def date_to_datetime_fields(env):
    openupgrade.date_to_datetime_tz(
        env.cr,
        "product_pricelist_item",
        "create_uid",
        openupgrade.get_legacy_name("date_end"),
        "date_end",
    )
    openupgrade.date_to_datetime_tz(
        env.cr,
        "product_pricelist_item",
        "create_uid",
        openupgrade.get_legacy_name("date_start"),
        "date_start",
    )


@openupgrade.migrate()
def migrate(env, version):
    date_to_datetime_fields(env)
    openupgrade.load_data(env.cr, "product", "14.0.1.2/noupdate_changes.xml")
