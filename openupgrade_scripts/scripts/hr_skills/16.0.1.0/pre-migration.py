from openupgradelib import openupgrade


def fill_skill_type_id_data(env):
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO hr_skill_type
        (name) VALUES ('Dummy Skill Type')
        RETURNING id;
        """,
    )

    skill_type_id = env.cr.fetchall()[0][0]

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_skill
        SET skill_type_id = %s
        WHERE skill_type_id IS NULL
        """,
        (skill_type_id,),
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_skill_type_id_data(env)
