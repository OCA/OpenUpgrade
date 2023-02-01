from openupgradelib import openupgrade, openupgrade_140


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "website_blog", "14.0.1.0/noupdate_changes.xml")
    openupgrade_140.convert_field_html_string_13to14(
        env,
        "blog.post",
        "content",
    )
