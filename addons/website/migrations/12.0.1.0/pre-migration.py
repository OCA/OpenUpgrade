# Copyright 2019 Eficent <http://www.eficent.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_field_renames = [
    ('website.page', 'website_page', 'website_published', 'is_published'),
]


def fill_website_company_id(cr):
    # done in pre-migration to avoid warning messages
    openupgrade.logged_query(
        cr, """
        UPDATE website w
        SET company_id = c.id
        FROM (SELECT id FROM res_company ORDER BY id ASC LIMIT 1) AS c
        WHERE w.company_id IS NULL
        """
    )


def fill_website_name(cr):
    # done in pre-migration to avoid warning messages
    openupgrade.logged_query(
        cr, """
        UPDATE website w
        SET name = 'Home #' || w.id
        WHERE w.name IS NULL
        """
    )


def fill_website_redirect_type(cr):
    # done in pre-migration to avoid warning messages
    openupgrade.logged_query(
        cr, """
        UPDATE website_redirect wr
        SET type = '301'
        WHERE wr.type IS NULL
        """
    )


def fill_website_redirect_urls(cr):
    # done in pre-migration to avoid warning messages
    openupgrade.logged_query(
        cr, """
        UPDATE website_redirect wr
        SET active = FALSE
        WHERE wr.url_from IS NULL OR wr.url_to IS NULL
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    openupgrade.rename_fields(env, _field_renames)
    fill_website_company_id(cr)
    fill_website_name(cr)
    fill_website_redirect_type(cr)
    fill_website_redirect_urls(cr)
