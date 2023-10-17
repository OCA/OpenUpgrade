# Copyright Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_translations_to_delete = [
    "digest_mail_layout",
    "digest_mail_main",
    "digest_tool_kpi",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "digest", "15.0.1.1/noupdate_changes.xml")
    openupgrade.delete_record_translations(env.cr, "digest", _translations_to_delete)
