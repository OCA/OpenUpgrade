
# Copyright 2020 Odoo Community Association (OCA)
# Copyright 2020 Opener B.V. <stefan@opener.am>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    # Cleanup potential duplicates
    openupgrade.logged_query(
        cr,
        """
        DELETE FROM mail_channel_partner mcp
        WHERE
            EXISTS (
                SELECT 1 FROM mail_channel_partner mcp2
                WHERE
                    mcp2.partner_id=mcp.partner_id
                    AND mcp2.channel_id=mcp.channel_id
                HAVING count(*) > 1
            )
            AND NOT EXISTS (
                SELECT 1 FROM ir_model_data imd
                WHERE
                    imd.model ='mail.channel.partner' and res_id = mcp.id
            )
        """,
    )
