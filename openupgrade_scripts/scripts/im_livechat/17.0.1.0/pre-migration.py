# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _discuss_channel_create_column(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE discuss_channel
            ADD COLUMN IF NOT EXISTS rating_last_value NUMERIC;
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _discuss_channel_create_column(env)
    # cannot use openupgrade.delete_sql_constraint_safely
    openupgrade.logged_query(
        env.cr,
        """ALTER TABLE discuss_channel
           DROP CONSTRAINT IF EXISTS mail_channel_livechat_operator_id""",
    )
    openupgrade.delete_records_safely_by_xml_id(
        env, ["im_livechat.constraint_mail_channel_livechat_operator_id"]
    )
