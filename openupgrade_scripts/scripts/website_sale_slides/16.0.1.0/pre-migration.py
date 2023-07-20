from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # update detailed_type of the course product
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_template pt
        SET detailed_type = 'course'
        FROM product_product pp
        JOIN slide_channel sc ON sc.product_id = pp.id
        WHERE pt.id = pp.product_tmpl_id
        """,
    )
