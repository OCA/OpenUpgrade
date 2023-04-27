from openupgradelib import openupgrade

from odoo.tools.json import scriptsafe as json_safe


def update_cover_properties_field(env):
    blog_post = env["blog.post"].search([])
    for post in blog_post:
        cover_properties = json_safe.loads(post.cover_properties)
        cover_properties["background_color_class"] = "o_cc3"
        cover_properties.pop("background-color", None)
        post.write({"cover_properties": json_safe.dumps(cover_properties)})


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "website_blog", "14.0.1.0/noupdate_changes.xml")
    update_cover_properties_field(env)
