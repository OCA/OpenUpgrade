# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from markupsafe import Markup
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    admin_channel = env.ref("mail.channel_admin")
    if admin_channel and any(
        c.account_peppol_proxy_state == "sender" for c in env["res.company"].search([])
    ):
        admin_channel.message_post(
            body=Markup(
                "<h1>Openupgrade v18: account_peppol</h1>"
                "<p>"
                "Cannot automatically determine res.company#peppol_external_provider."
                "You should fill this field manually or rerun the peppol wizard."
                "</p>"
            )
        )
