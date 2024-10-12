# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _ir_act_server_update_base_automation_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE ir_act_server
            ADD COLUMN IF NOT EXISTS base_automation_id INTEGER;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_act_server ias
            SET base_automation_id = ba.id
        FROM base_automation ba
        WHERE ba.action_server_id = ias.id
        """,
    )


def _base_automation_sync_from_ir_act_server(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE base_automation
            ADD COLUMN IF NOT EXISTS model_id INTEGER,
            ADD COLUMN IF NOT EXISTS name JSONB;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE base_automation ba
            SET model_id = ias.model_id,
                name = ias.name
        FROM ir_act_server ias
        WHERE ba.action_server_id = ias.id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _ir_act_server_update_base_automation_id(env)
    _base_automation_sync_from_ir_act_server(env)
