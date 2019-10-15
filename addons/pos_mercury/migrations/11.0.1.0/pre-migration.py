# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.set_xml_ids_noupdate_value(
        env, 'pos_mercury', ['barcode_rule_credit'], True)
