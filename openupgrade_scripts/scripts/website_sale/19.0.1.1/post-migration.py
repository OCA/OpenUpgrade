# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_deleted_xmlids = [
    "website_sale.product_attribute_brand",
]


def product_ribbon_sequence(env):
    """
    Set sequence to id where it hasn't been set yet
    """
    env.cr.execute("UPDATE product_ribbon SET sequence=id WHERE sequence IS NULL")


def website_checkout_steps(env):
    """
    Create checkout steps for each website
    """
    for website in env["website"].search([]):
        website._create_checkout_steps()


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "website_sale", "19.0.1.1/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "website_sale",
        ["mail_template_sale_cart_recovery"],
        ["body_html"],
    )
    product_ribbon_sequence(env)
    website_checkout_steps(env)
    openupgrade.delete_records_safely_by_xml_id(env, _deleted_xmlids)
