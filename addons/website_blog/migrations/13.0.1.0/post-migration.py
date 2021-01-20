# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import json

from openupgradelib import openupgrade


def _preserve_post_covers(env):
    """Preserve how blog post covers display.

    Performs these transformations to preserve blog post cover sizes:

    * Full size:
      .cover.container-fluid.cover_full ➡ .o_record_has_cover.cover_full
    * Medium size:
      .cover.container-fluid.cover_narrow ➡ .o_record_has_cover.cover_mid
    * Narrow size:
      .cover.container.cover_narrow ➡ .o_record_has_cover.cover_auto
    """
    posts = env["blog.post"].search([("cover_properties", "!=", False)])
    for post in posts:
        properties = json.loads(post.cover_properties)
        resize_classes = set(properties.get("resize_class", "").split())
        if "cover" in resize_classes:
            resize_classes.add("o_record_has_cover")
            # Mid
            if {"container-fluid", "cover_narrow"} <= resize_classes:
                resize_classes.add("cover_mid")
            # Narrow
            elif {"container", "cover_narrow"} <= resize_classes:
                resize_classes.add("cover_auto")
            resize_classes.difference_update({"cover", "container", "container-fluid"})
            post.write(
                {
                    "cover_properties": json.dumps(
                        dict(properties, resize_class=list(resize_classes))
                    )
                }
            )


@openupgrade.migrate()
def migrate(env, version):
    _preserve_post_covers(env)
    openupgrade.delete_records_safely_by_xml_id(
        env, [
            "website_blog.blog_post_cover_01",
            "website_blog.blog_post_cover_02",
        ]
    )
