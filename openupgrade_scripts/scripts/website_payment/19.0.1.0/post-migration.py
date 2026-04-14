# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_deleted_xmlids = [
    "website_payment.mail_template_donation",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(env, _deleted_xmlids)
