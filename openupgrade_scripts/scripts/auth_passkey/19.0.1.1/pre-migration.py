# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

noupdate_xmlids = [
    "rule_auth_passkey_key_admin",
    "rule_auth_passkey_key_user",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.set_xml_ids_noupdate_value(env, "auth_passkey", noupdate_xmlids, True)
