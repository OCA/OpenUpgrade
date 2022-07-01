from openupgradelib import openupgrade


def _create_crm_team_member(env):
    """user admin will automatic create crm_team_member by crm_team_data.xml"""
    user_admin = env.ref("base.user_admin")
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO crm_team_member (user_id, crm_team_id, active)
        SELECT id, sale_team_id, True
        FROM res_users
        WHERE sale_team_id IS NOT NULL AND id != %s
        """
        % (user_admin.id),
    )


@openupgrade.migrate()
def migrate(env, version):
    _create_crm_team_member(env)
