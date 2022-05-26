# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def _map_crm_team_id(env):
    """From now on, every pos.order will have stored its crm.team relation, so if it's
    changed later, those sales don't go to the new team. Anyway we have to map it in
    the old orders so we don't loose that info in the sales report."""
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE pos_order po
        SET crm_team_id = pc.crm_team_id
        FROM pos_config pc, pos_session ps
        WHERE
            ps.id = po.session_id
            AND pc.id = ps.config_id
            AND po.crm_team_id IS NULL
            AND pc.crm_team_id IS NOT NULL
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, "pos_sale", "migrations/13.0.1.0/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(
        env, [
            "point_of_sale.pos_config_main",
        ]
    )
    _map_crm_team_id(env)
