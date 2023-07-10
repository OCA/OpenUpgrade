# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_translations_to_delete = [
    "digest_mail_layout",
    "digest_section_mobile",
    "digest_tip_digest_0",
    "digest_tip_digest_1",
    "digest_tip_digest_2",
    "digest_tip_digest_3",
    "digest_tip_digest_4",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "digest", "16.0.1.1/noupdate_changes.xml")
    openupgrade.delete_record_translations(env.cr, "digest", _translations_to_delete)
