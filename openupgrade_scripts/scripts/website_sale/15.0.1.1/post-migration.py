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


def enable_price_filter_view(env):
    """If you had website_sale_attribute_filter_price module installed in previous
    version, replace it by the new core price filter.
    """
    for website in env["website"].search([]):
        view = env["ir.ui.view"].search(
            [
                ("key", "=", "website_sale_attribute_filter_price.pricefilter"),
                ("website_id", "=", website.id),
            ]
        )
        if view:
            # It's important to set the context to create the new view related to the
            # current website. See write method of ir.ui.view in website module
            website.with_context(website_id=website.id).viewref(
                "website_sale.filter_products_price"
            ).active = True
            view.unlink()


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
    enable_price_filter_view(env)
