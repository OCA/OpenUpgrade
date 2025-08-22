# Copyright 2025 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "website_sale_picking", "17.0.1.0/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "website_sale_picking",
        ["onsite_delivery_product"],
        ["description"],
    )
