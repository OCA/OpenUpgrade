from openupgradelib import openupgrade

from odoo.tools.json import scriptsafe as json_safe


def update_cover_properties_field(env, records):
    for record in records:
        cover_properties = json_safe.loads(record.cover_properties)
        cover_properties["background_color_class"] = "o_cc3"
        cover_properties.pop("background-color", None)
        record.write({"cover_properties": json_safe.dumps(cover_properties)})


def blog_post_update_cover_properties_field(env):
    blog_post = env["blog.post"].search([])
    update_cover_properties_field(env, blog_post)


def blog_blog_update_cover_properties_field(env):
    blog_blog = env["blog.blog"].search([])
    update_cover_properties_field(env, blog_blog)


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "website_blog", "14.0.1.0/noupdate_changes.xml")
    blog_post_update_cover_properties_field(env)
    blog_blog_update_cover_properties_field(env)
