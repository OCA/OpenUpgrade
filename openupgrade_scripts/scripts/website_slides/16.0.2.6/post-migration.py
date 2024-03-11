# Copyright 2023 Viindoo - Nguyễn Việt Lâm
# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def _fill_source_type_external(env):
    """Switch to external for those with `google_drive_id`, that are the only where
    these applies:
    https://github.com/odoo/odoo/blob/42bcc3ef284ca355e2323641176573b53e7d2e28/addons/
    website_slides/controllers/main.py#L1197
    """
    env["slide.slide"].search([]).filtered("google_drive_id").source_type = "external"


def _fill_nbr_article(env):
    """Fill the values recreating the compute method, but only for the field
    nbr_article.
    """
    for source in ["slide", "channel"]:
        if source == "slide":
            records = env["slide.slide"].search([("is_category", "=", True)])
            field = "category_id"
        else:
            records = env["slide.channel"].search([])
            field = "channel_id"
        domain = [
            ("is_published", "=", True),
            ("is_category", "=", False),
            (field, "in", records.ids),
        ]
        res = env["slide.slide"]._read_group(
            domain,
            [field, "slide_category"],
            [field, "slide_category"],
            lazy=False,
        )
        category_stats = records._compute_slides_statistics_category(res)
        for record in records:
            record.nbr_article = category_stats.get(
                record._origin.id, {"nb_article": 0}
            )["nbr_article"]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "website_slides", "16.0.2.6/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "website_slides",
        [
            "mail_template_channel_completed",
            "mail_template_slide_channel_invite",
        ],
        ["name", "subject", "description"],
    )
    openupgrade.delete_record_translations(
        env.cr,
        "website_slides",
        ["mail_template_slide_channel_invite"],
        ["name", "description"],
    )
    openupgrade.delete_record_translations(
        env.cr,
        "website_slides",
        ["slide_template_published", "slide_template_shared"],
    )
    _fill_source_type_external(env)
    _fill_nbr_article(env)
