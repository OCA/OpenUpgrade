# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Switch to noupdate=0 for getting the current v16 arch, for switching in post again
    openupgrade.set_xml_ids_noupdate_value(env, "digest", ["digest_mail_layout"], False)
