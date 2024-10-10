# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_deleted_xml_records = [
    "base.res_partner_rule_private_employee",
    "base.res_partner_rule_private_group",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "base", "17.0.1.3/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(
        env,
        _deleted_xml_records,
    )
