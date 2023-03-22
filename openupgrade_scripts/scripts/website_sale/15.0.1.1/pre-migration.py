from openupgradelib import openupgrade


def enable_price_filter_view(env):
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
    enable_price_filter_view(env)
