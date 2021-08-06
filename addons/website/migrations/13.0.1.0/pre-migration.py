# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_model_renames = [
    ('website.redirect', 'website.rewrite'),
]

_table_renames = [
    ('website_redirect', 'website_rewrite'),
]

_field_renames = [
    ('website.rewrite', 'website_rewrite', 'type', 'redirect_type'),
]

_xmlid_renames = [
    ('website.access_website_redirect', 'website.access_website_rewrite'),
    ('website.access_website_redirect_designer', 'website.access_website_rewrite_designer'),
]


def fill_website_rewrite_name(cr):
    openupgrade.logged_query(
        cr, """
        ALTER TABLE website_rewrite
        ADD COLUMN name varchar""",
    )
    openupgrade.logged_query(
        cr, """
        UPDATE website_rewrite
        SET name = CASE WHEN url_from IS NOT NULL OR url_to IS NOT NULL THEN
            url_from || ' -> ' || url_to
            ELSE 'default_name' END""",
    )


def remove_social_googleplus(env):
    """On v13, this field has been removed, but it was put on certain places on
    the website, and they remain unaltered due to the noupdate=1 flag or being
    a COW (created on write) view, so we directly remove that part from the
    view if we find the exact HTML expected code that is on the definition.
    This is done for avoiding side effects, and it means that if you have altered
    somehow that part, you will need to remove it manually.
    """
    for key, code in [
        (
            "website.footer_custom",
            '                                <a t-if="website.social_googleplus" t-att-href="website.social_googleplus"'
            ' class="btn btn-sm btn-link" rel="publisher"><i class="fa fa-2x fa-google-plus-square"/></a>\n'
        ),
        (
            "website.footer_default",
            '                        <a t-att-href="website.social_googleplus" t-if="website.social_googleplus" '
            'rel="publisher"><i class="fa fa-google-plus-square"/></a>\n'
        ),
        (
            "website_blog.opt_blog_rc_follow_us",
            '                <a t-att-href="website.social_googleplus" t-if="website.social_googleplus" '
            'aria-label="Google Plus" title="Google Plus"><i class="fa fa-google-plus-square"/></a>\n'
        ),
        (
            "website_mass_mailing.social_links",
            '    <t t-if="website.social_googleplus">\n'
            '        <a t-att-href="website.social_googleplus" style="margin-left:10px" '
            'aria-label="Google Plus" title="Google Plus">\n'
            '            <span class="fa fa-google-plus"/>\n'
            '        </a>\n'
            '    </t>\n'
        ),
    ]:
        views = env["ir.ui.view"].search([("key", "=", key)])
        for view in views:
            arch = view.arch.replace(code, "")
            if arch != view.arch:
                view.arch = arch


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(env.cr, _model_renames)
    openupgrade.rename_tables(env.cr, _table_renames)
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    fill_website_rewrite_name(env.cr)
    openupgrade.cow_templates_mark_if_equal_to_upstream(env.cr)
    remove_social_googleplus(env)
