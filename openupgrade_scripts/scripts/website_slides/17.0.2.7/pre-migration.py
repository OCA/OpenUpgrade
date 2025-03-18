# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def precreate_slide_channel_partner_active(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE slide_channel_partner
        ADD COLUMN IF NOT EXISTS active boolean DEFAULT true
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE slide_channel_partner ALTER COLUMN active DROP DEFAULT
        """,
    )


def fill_slide_channel_partner_member_status(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE slide_channel_partner
        ADD COLUMN IF NOT EXISTS member_status varchar
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE slide_channel_partner
        SET member_status = CASE WHEN completed OR completion = 100 THEN 'completed'
            WHEN completion = 0 OR completion IS NULL THEN 'joined'
            ELSE 'ongoing' END
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    precreate_slide_channel_partner_active(env)
    fill_slide_channel_partner_member_status(env)
