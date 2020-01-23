# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade, openupgrade_120
from openupgradelib.openupgrade_tools import convert_html_fragment,\
    convert_html_replacement_class_shortcut as _r


def replace_old_snippet_reference(env):
    """
    This method change the external identifier from snippet_latest_posts to
    website_blog for all views that render this snippet
    """
    views_with_snippet = env['ir.ui.view'].with_context(
        active_test=False
    ).search([
        ('arch_db', 'ilike', 'snippet_latest_posts'),
    ])
    for view in views_with_snippet:
        replacement = (
            _r(selector="div",
               attr_rm="snippet_latest_posts."
                       "s_latest_posts_big_picture_template",
               attr_add={
                   "data-template":
                       "website_blog.s_latest_posts_big_picture_template"}),
        )
        new_content = convert_html_fragment(view.arch_db, replacement)
        view.arch = new_content


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, 'website_blog', 'migrations/12.0.1.0/noupdate_changes.xml')
    openupgrade_120.convert_field_bootstrap_3to4(
        env, 'blog.post', 'content',
    )
    replace_old_snippet_reference(env)
