# -*- coding: utf-8 -*-
# © 2017 Bloopark - Cesar Lage
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_xmlid_renames = [
    ('report.action_report_externalpreview', 'web.action_report_externalpreview'),
    ('report.action_report_internalpreview', 'web.action_report_internalpreview'),
    ('report.external_layout', 'web.external_layout'),
    ('report.html_container', 'web.html_container'),
    ('report.internal_layout', 'web.internal_layout'),
    ('report.minimal_layout', 'web.minimal_layout'),
    ('report.preview_internalreport', 'web.preview_internalreport'),
    ('report.preview_externalreport', 'web.preview_externalreport'),
    ('report.assets_common', 'web.report_assets_common'),
    ('report.assets_editor', 'web.report_assets_editor'),
    ('report.assets_pdf', 'web.report_assets_pdf'),
    ('report.layout', 'web.report_layout'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
