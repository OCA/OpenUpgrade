# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from itertools import product

from openupgradelib import openupgrade
from openupgradelib.openupgrade_tools import (
    convert_html_fragment,
    convert_html_replacement_class_shortcut as _r,
)

_BG_SIZES = ("25%", "50%", "75%", "auto")
REPLACEMENTS = [
    # Replacements to remove website_img_bg_style
    _r("bg-center-h bg-bottom", "oe_img_bg o_bg_img_opt_custom",
       styles={"background-position": "50% 100%"}),
    _r("bg-center-h bg-top", "oe_img_bg o_bg_img_opt_custom",
       styles={"background-position": "50% 0%"}),
    _r("bg-center-v bg-left", "oe_img_bg o_bg_img_opt_custom",
       styles={"background-position": "0% 50%"}),
    _r("bg-center-v bg-right", "oe_img_bg o_bg_img_opt_custom",
       styles={"background-position": "100% 50%"}),
    _r("bg-left bg-bottom", "oe_img_bg o_bg_img_opt_custom",
       styles={"background-position": "0% 100%"}),
    _r("bg-left bg-top", "oe_img_bg o_bg_img_opt_custom",
       styles={"background-position": "0% 0%"}),
    _r("bg-right bg-bottom", "oe_img_bg o_bg_img_opt_custom",
       styles={"background-position": "100% 100%"}),
    _r("bg-right bg-top", "oe_img_bg o_bg_img_opt_custom",
       styles={"background-position": "100% 0%"}),
    _r("bg-size-contain-v", "oe_img_bg o_bg_img_opt_contain"),
    _r("bg-size-contain-v", "oe_img_bg o_bg_img_opt_contain"),
    _r("bg-size-cover-v", "oe_img_bg"),
    _r("bg-size-cover-v", "oe_img_bg"),
    _r("bg-size-no-repeat-h"),
    _r("bg-size-no-repeat-v"),
    _r("bg-size-repeat-h bg-size-repeat-v",
       "oe_img_bg o_bg_img_opt_custom o_bg_img_opt_repeat"),
    _r("bg-size-repeat-h",
       "oe_img_bg o_bg_img_opt_custom o_bg_img_opt_repeat_x"),
    _r("bg-size-repeat-v",
       "oe_img_bg o_bg_img_opt_custom o_bg_img_opt_repeat_y"),
]

for h, v in product(_BG_SIZES, _BG_SIZES):
    REPLACEMENTS.append(_r(
        "bg-size-%s-h bg-size-%s-v" % (h.strip("%"), v.strip("%")),
        "oe_img_bg o_bg_img_opt_custom",
        styles={"background-size": "%s %s" % (h, v)}))


def update_website_views(env):
    """Handle removal of website_img_bg_style module."""
    # Find report views, which should never be converted here
    report_names = env["ir.actions.report.xml"].search([
        ("report_name", "!=", False),
        ("report_type", "=like", "qweb-%"),
    ]).mapped("report_name")
    # Find updatable views, to be excluded; standard addon update is enough
    udpatable_ids = env["ir.model.data"].search([
        ("model", "=", "ir.ui.view"),
        ("noupdate", "=", False),
    ]).mapped("res_id")
    # Find views to convert
    all_views = env['ir.ui.view'].search([
        ("active", "=", True),
        ("id", "not in", udpatable_ids),
        ("key", "not in", report_names),
        ("type", "=", "qweb"),
    ])
    # Apply conversions
    for view in all_views:
        old_content = view.arch
        new_content = convert_html_fragment(old_content, REPLACEMENTS)
        if old_content != new_content:
            view.arch = new_content


@openupgrade.migrate()
def migrate(env, version):
    # rename groups' xmlids
    openupgrade.rename_xmlids(env.cr, [
        ('base.group_website_designer', 'website.group_website_designer'),
        ('base.group_website_publisher', 'website.group_website_publisher'),
    ])
    # clean out group assignments for qweb views
    env.cr.execute(
        "delete from ir_ui_view_group_rel "
        "where view_id in (select id from ir_ui_view where type='qweb')"
    )
    update_website_views(env)
