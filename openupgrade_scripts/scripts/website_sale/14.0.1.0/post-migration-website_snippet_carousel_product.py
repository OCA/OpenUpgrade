# Copyright 2022 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import uuid

from lxml import etree
from openupgradelib import openupgrade


def prepare_dynamic_carousel(defaults_dict):
    return """
<section
    data-snippet="s_dynamic_snippet"
    class="s_dynamic_snippet_carousel s_dynamic pt24 pb24 o_colored_level d-none"
    data-name="Dynamic Carousel"
    data-number-of-elements="{products_per_slide}"
    data-number-of-elements-small-devices="1"
    data-carousel-interval="{interval}"
    data-filter-id="{filter}"
    data-number-of-records="{products_limit}"
    data-template-key="website.dynamic_filter_template_image_title_footer"
    {extra_attribs}
>
    <div class="container o_not_editable">
        <div class="css_non_editable_mode_hidden" />
        {previous_xml}
        <div class="dynamic_snippet_template"/>
        {next_xml}
    </div>
</section>
    """.format(
        **defaults_dict
    )


def update_carousels(env, views_with_carousel):
    # For each view analyze and extract the snippet
    default_snippet_filter = env.ref("website_sale.dynamic_filter_demo_products")
    for view in views_with_carousel:
        tree = etree.fromstring(view.arch_db)
        carousels = tree.xpath("//section[hasclass('s_product_carousel')]")
        for carousel in carousels:
            try:
                data = tree.xpath("//*[hasclass('js_product_carousel')]")[0]
            except IndexError:
                continue
            # The snnipet could have relevant extra attributes like t-if
            carousel.attrib.pop("class")
            extra_attribs = " ".join({f"{a}='{v}'" for a, v in carousel.attrib.items()})
            # If there are sibling elements, we'd like to append keep them in the final
            # carousel
            previous_xml = next_xml = ""
            if data.getprevious() is not None:
                previous_xml = etree.tostring(data.getprevious(), encoding="unicode")
            if data.getnext() is not None:
                next_xml = etree.tostring(data.getnext(), encoding="unicode")
            # We'll use the dynamic widget if the carousel has a domain. Otherwise we'll
            # use the regular product carousel.
            domain = data.attrib.get("data-domain")
            # Apply default values when they aren't declared
            defaults_dict = {
                "products_limit": data.attrib.get("data-products-limit", 16),
                "products_per_slide": data.attrib.get("data-products-per-slide", 4),
                "interval": data.attrib.get("data-interval", 5000),
                "previous_xml": previous_xml,
                "next_xml": next_xml,
                "extra_attribs": extra_attribs,
            }
            # To use domains we need to create a website snippet filter and link it to
            # the proper values. When no domain is set, we can rely on Odoo's defaults.
            # Otherwise, we have to prepare the proper filter.
            if not domain:
                defaults_dict["filter"] = default_snippet_filter.id
            else:
                carousel_filter = env["ir.filters"].create(
                    {
                        "name": "Filter {} - {}".format(
                            carousel.attrib.get("data-name", uuid.uuid4().hex[:6]),
                            view.id,
                        ),
                        "model_id": "product.product",
                        "user_id": False,
                        "domain": domain,
                    }
                )
                snippet_filter = env.ref(
                    "website_sale.dynamic_filter_demo_products"
                ).copy(
                    {
                        "name": "{} - {}".format(
                            carousel.attrib.get("data-name"), view.id
                        ),
                        "action_server_id": False,
                        "website_id": view.website_id.id,
                        "filter_id": carousel_filter.id,
                    }
                )
                defaults_dict["filter"] = snippet_filter.id
            updated_snippet = etree.fromstring(prepare_dynamic_carousel(defaults_dict))
            carousel.getparent().replace(carousel, updated_snippet)
        view.arch_db = etree.tostring(tree)


@openupgrade.migrate()
def migrate(env, version):
    if not env.ref("website_sale.s_product_carousel", raise_if_not_found=False):
        return
    # Search views with the snippet applied. If no views are found, no carousels will
    # be changed
    views_with_carousel = env["ir.ui.view"].search(
        [
            ("website_id", "!=", False),
            ("arch_db", "ilike", "<section %s_product_carousel"),
        ]
    )
    update_carousels(env, views_with_carousel)
