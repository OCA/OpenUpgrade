# Copyright 2019 Eficent <http://www.eficent.com>
# Copyright 2020 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade, openupgrade_120
from openupgradelib.openupgrade_tools import convert_html_fragment,\
    convert_html_replacement_class_shortcut as _r

_SNIPPET_BLOG_POST_REPLACEMENTS = (
    _r(selector='div[data-template="snippet_latest_posts.'
                'media_list_template"]',
       attr_rm={"data-template"},
       attr_add={
           "data-template": "website_blog.s_latest_posts_list_template",
       }),
    _r(selector='div[data-template="snippet_latest_posts.'
                's_latest_posts_big_picture_template"]',
       attr_rm={"data-template"},
       attr_add={
           "data-template":
               "website_blog.s_latest_posts_big_picture_template"}),
    _r(selector='.js_get_posts', class_add='row s_col_no_bgcolor'),
    _r(selector='.post .media .media_list_template',
       class_rm='.post .media .media_list_template',
       class_add='col-12 media mt-3 s_latest_posts_post'),
)


def old_snippet_conversion(env):
    """
    This method change the external identifier from snippet_latest_posts to
    website_blog for all views that render this snippet.
    Adds row class to div js_get_posts, needed in v12.0
    """
    views_with_snippet = env['ir.ui.view'].with_context(
        active_test=False
    ).search([
        ('arch_db', 'ilike', 'snippet_latest_posts'),
    ])
    for view in views_with_snippet:
        view.arch_db = convert_html_fragment(
            view.arch_db, _SNIPPET_BLOG_POST_REPLACEMENTS)


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, 'website_blog', 'migrations/12.0.1.0/noupdate_changes.xml')
    openupgrade_120.convert_field_bootstrap_3to4(
        env, 'blog.post', 'content',
    )
    old_snippet_conversion(env)
