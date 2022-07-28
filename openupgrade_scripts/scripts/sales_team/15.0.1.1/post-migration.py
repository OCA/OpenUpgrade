from openupgradelib import openupgrade


def _create_crm_team_member(env):
    """user admin will automatically create crm_team_member by crm_team_data.xml"""
    user_admin = env.ref("base.user_admin")
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO crm_team_member AS ctm (user_id, crm_team_id, active,
            create_uid, write_uid, create_date, write_date)
        SELECT ru.id, ru.sale_team_id, TRUE,
            GREATEST(ru.write_uid, ct.write_uid),
            GREATEST(ru.write_uid, ct.write_uid),
            GREATEST(ru.write_date, ct.write_date),
            GREATEST(ru.write_date, ct.write_date)
        FROM res_users ru
        JOIN crm_team ct ON ru.sale_team_id = ct.id
        WHERE ru.id != %s
        RETURNING ctm.id
        """,
        (user_admin.id,),
    )
    member_ids = [x[0] for x in env.cr.fetchall()]
    if member_ids and not env["ir.config_parameter"].sudo().get_param(
        "sales_team.membership_multi", False
    ):
        env["crm.team.member"]._synchronize_memberships(
            [
                dict(
                    user_id=membership.user_id.id, crm_team_id=membership.crm_team_id.id
                )
                for membership in env["crm.team.member"].browse(member_ids)
            ]
        )


@openupgrade.migrate()
def migrate(env, version):
    _create_crm_team_member(env)
