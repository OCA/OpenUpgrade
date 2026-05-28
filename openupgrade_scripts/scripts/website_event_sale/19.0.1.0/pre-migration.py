from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM ir_rule WHERE id IN (
            SELECT imd.res_id FROM ir_model_data imd
            WHERE imd.model = 'ir.rule'
              AND imd.module = 'website_event_sale'
              AND imd.name = 'event_product_template_public'
        )
        """,
    )
