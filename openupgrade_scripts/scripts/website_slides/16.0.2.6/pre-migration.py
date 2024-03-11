# Copyright 2023 Viindoo - Nguyễn Việt Lâm
# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

renamed_fields = [
    ("slide.slide", "slide_slide", "datas", "binary_content"),
    ("slide.channel", "slide_channel", "share_template_id", "share_slide_template_id"),
]
xml_ids_to_rename = [
    (
        "website_slides.rule_slide_slide_resource_manager",
        "website_slides.rule_slide_slide_resource_downloadable_manager",
    ),
]


def _create_and_fill_data_from_slide_type_to_slide_category(env):
    openupgrade.copy_columns(
        env.cr, {"slide_slide": [("slide_type", "slide_category", None)]}
    )
    openupgrade.map_values(
        env.cr,
        "slide_type",
        "slide_category",
        [("webpage", "article"), ("presentation", "document")],
        table="slide_slide",
    )
    openupgrade.rename_columns(env.cr, {"slide_slide": [("slide_type", None)]})


def _create_and_fill_data_for_source_type(env):
    openupgrade.logged_query(
        env.cr,
        "ALTER TABLE slide_slide ADD COLUMN IF NOT EXISTS source_type VARCHAR",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE slide_slide
        SET source_type = CASE
            WHEN url IS NOT NULL AND slide_category = 'document' THEN 'external'
            ELSE 'local_file'
        END
        """,
    )


def _create_column_and_migrate_data_from_slide_link_to_slide_resource(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE slide_slide_resource
        ADD COLUMN IF NOT EXISTS link VARCHAR,
        ADD COLUMN IF NOT EXISTS resource_type VARCHAR
        """,
    )
    openupgrade.logged_query(
        env.cr,
        "UPDATE slide_slide_resource SET resource_type = 'file'",
    )
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO slide_slide_resource
        (name, link, slide_id, resource_type)
        SELECT name, link, slide_id, 'url'
        FROM slide_slide_link
        """,
    )


def _create_nbr_article(env):
    """Pre-create and fill these fields for avoiding KeyError crashes as the compute
    method uses read_group.
    """
    openupgrade.logged_query(
        env.cr,
        "ALTER TABLE slide_channel ADD COLUMN IF NOT EXISTS nbr_article INT4",
    )
    openupgrade.logged_query(
        env.cr,
        "ALTER TABLE slide_slide ADD COLUMN IF NOT EXISTS nbr_article INT4 DEFAULT 0",
    )
    openupgrade.logged_query(
        env.cr,
        "ALTER TABLE slide_slide ALTER COLUMN nbr_article DROP DEFAULT",
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, renamed_fields)
    openupgrade.rename_xmlids(env.cr, xml_ids_to_rename)
    _create_and_fill_data_from_slide_type_to_slide_category(env)
    _create_column_and_migrate_data_from_slide_link_to_slide_resource(env)
    _create_and_fill_data_for_source_type(env)
    _create_nbr_article(env)
