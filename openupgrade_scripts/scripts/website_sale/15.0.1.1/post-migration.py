from openupgradelib import openupgrade


def set_visibility_product_attribute(env):
    # Check that website_sale_product_attribute_filter_visibility was installed
    if not openupgrade.column_exists(env.cr, "product_attribute", "is_published"):
        return
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_attribute
        SET visibility = CASE WHEN is_published is not true THEN 'hidden'
                              ELSE 'visible'
                              END
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    # Load noupdate changes
    openupgrade.load_data(
        env.cr,
        "website_sale",
        "15.0.1.1/noupdate_changes.xml",
    )
    openupgrade.delete_record_translations(
        env.cr,
        "website_sale",
        [
            "mail_template_sale_cart_recovery",
        ],
    )
    set_visibility_product_attribute(env)
