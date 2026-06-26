# Copyright 2026 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "auth_oauth", "19.0.1.0/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "auth_oauth",
        ["provider_facebook", "provider_google", "provider_openerp"],
        ["body"],
    )
