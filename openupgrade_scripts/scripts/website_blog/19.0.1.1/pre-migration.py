# Copyright 2026 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_new_columns = [
    ("blog.blog", "sequence", "integer", None, "blog_blog"),
    ("blog.blog", "is_seo_optimized", "boolean", False, "blog_blog"),
    ("blog.post", "is_seo_optimized", "boolean", False, "blog_post"),
    ("blog.tag", "is_seo_optimized", "boolean", False, "blog_tag"),
]


def _fill_blog_is_seo_optimized(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE blog_blog
        SET is_seo_optimized = True
        WHERE website_meta_title IS NOT NULL
            AND website_meta_description IS NOT NULL
            AND website_meta_keywords IS NOT NULL
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE blog_post
        SET is_seo_optimized = True
        WHERE website_meta_title IS NOT NULL
            AND website_meta_description IS NOT NULL
            AND website_meta_keywords IS NOT NULL
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE blog_tag
        SET is_seo_optimized = True
        WHERE website_meta_title IS NOT NULL
            AND website_meta_description IS NOT NULL
            AND website_meta_keywords IS NOT NULL
        """,
    )


def _fill_blog_blog_sequence(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE blog_blog AS bb
        SET sequence = sequence_data.sequence
        FROM (
            SELECT
                id,
                row_number() OVER (ORDER BY create_date ASC, id ASC) AS sequence
            FROM blog_blog
        ) AS sequence_data
        WHERE bb.id = sequence_data.id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.add_columns(env, _new_columns)
    _fill_blog_is_seo_optimized(env)
    _fill_blog_blog_sequence(env)
