from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version=None):
    """
    Set consumed tours from legacy table after migration and
    remove obsolete security rules.
    """
    openupgrade.logged_query(
        env.cr,
        f"""
        INSERT INTO res_users_web_tour_tour_rel
        (res_users_id, web_tour_tour_id)
        SELECT legacy_table.user_id, web_tour_tour.id
        FROM
        {openupgrade.get_legacy_name('web_tour_tour')} legacy_table,
        web_tour_tour
        WHERE web_tour_tour.name=legacy_table.name
        ON CONFLICT DO NOTHING
        """,
    )

    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM ir_rule
        WHERE model_id = (
            SELECT id FROM ir_model WHERE model = 'web_tour.tour'
        )
        AND domain_force LIKE '%user_id%';
        """,
    )
