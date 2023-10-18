# Copyright 2023 Tecnativa - Víctor Martínez
# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_translations_to_delete = [
    "name",
    "description",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "website_profile", "16.0.1.0/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "website_profile",
        ["validation_email"],
        ["name", "description"],
    )
