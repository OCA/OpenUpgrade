# Copyright 2023 Coop IT Easy SC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def _set_published_state(env):
    """Set published state according to the provider state as that will keep the former
    visibility state"""
    env["payment.provider"].search([("state", "=", "enabled")]).is_published = True


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "payment", "16.0.2.0/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "payment.payment_acquirer_alipay",
            "payment.payment_acquirer_ogone",
            "payment.payment_acquirer_payulatam",
            "payment.payment_acquirer_payumoney",
            "payment.payment_acquirer_test",
        ],
    )
    _set_published_state(env)
