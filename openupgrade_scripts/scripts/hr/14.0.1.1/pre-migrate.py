# Copyright 2022 Marcin Żurawski
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM ir_ui_view
        WHERE inherit_id=(
            SELECT res_id
            FROM ir_model_data
            WHERE name='res_users_view_form_profile' AND module='hr'
        );
        """
    )
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM ir_ui_view
        WHERE id=(
            SELECT res_id
            FROM ir_model_data
            WHERE name='res_users_view_form_profile' AND module='hr'
        );
        """
    )
