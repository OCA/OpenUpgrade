# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_field_renames = [
    ('slide.channel', 'slide_channel', 'description', 'description_html'),
    ('slide.channel', 'slide_channel', 'total', 'total_slides'),
    ('slide.channel', 'slide_channel', 'nbr_videos', 'nbr_video'),
    ('slide.channel', 'slide_channel', 'nbr_documents', 'nbr_document'),
    ('slide.channel', 'slide_channel', 'nbr_infographics', 'nbr_infographic'),
    ('slide.channel', 'slide_channel', 'nbr_presentations', 'nbr_presentation'),
    ('slide.channel', 'slide_channel', 'group_ids', 'enroll_group_ids'),
    ('slide.channel', 'slide_channel', 'access_error_msg', 'enroll_msg'),
]

_column_renames = {
    "slide_slide": [
        ("category_id", None),
    ],
    "slide_channel": [
        ("visibility", None),
        ("promote_strategy", None),
    ],
    # m2m table before renaming it
    "rel_channel_groups": [
        ("channel_id", "slide_channel_id"),
        ("group_id", "res_groups_id"),
    ]
}

_column_copies = {
    "slide_slide": [
        ("likes", None, None),
        ("dislikes", None, None),
        ("slide_views", None, None),
    ],
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(env.cr, _column_renames)
    openupgrade.copy_columns(env.cr, _column_copies)
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.logged_query(env.cr, "ALTER TABLE slide_slide ADD COLUMN category_id int4")
    openupgrade.rename_tables(env.cr, [("rel_channel_groups", "res_groups_slide_channel_rel")])
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "website_slides",
        [
            "rule_slide_channel_global",
            "rule_slide_slide_global",
        ],
        False,
    )
    openupgrade.add_fields(env, [("user_id", "slide.channel", "slide_channel", "many2one", False, "website_slides")])
