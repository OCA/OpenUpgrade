from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM ir_rule WHERE id IN (
            SELECT imd.res_id FROM ir_model_data imd
            WHERE imd.model = 'ir.rule'
              AND imd.module = 'website_membership'
              AND imd.name IN (
                  'membership_membership_line_public',
                  'membership_product_product_public'
              )
        )
        """,
    )
