# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_field_renames = [
    # slide.slide
    ('slide.slide', 'slide_slide', 'index_content', 'html_content'),
    # slide.channel
    ('slide.channel', 'slide_channel', 'total', 'total_slides'),
    ('slide.channel', 'slide_channel', 'nbr_videos', 'nbr_video'),
    ('slide.channel', 'slide_channel', 'nbr_documents', 'nbr_document'),
    ('slide.channel', 'slide_channel', 'nbr_infographics', 'nbr_infographic'),
    ('slide.channel', 'slide_channel', 'nbr_presentations', 'nbr_presentation'),
    ('slide.channel', 'slide_channel', 'group_ids', 'enroll_group_ids'),
    ('slide.channel', 'slide_channel', 'access_error_msg', 'enroll_msg'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "website_slides",
        [
            "rule_slide_channel_global",
            "rule_slide_slide_global",
        ],
        False,
    )
