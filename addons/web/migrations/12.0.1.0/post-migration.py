# Copyright 2018 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from psycopg2.extensions import AsIs
from openupgradelib import openupgrade


def fill_res_company_external_report_layout_id(cr):
    """Fill external_report_layout_id of res_company"""

    values = {'external_report_layout': AsIs(
        openupgrade.get_legacy_name('external_report_layout'))}
    cr.execute(
        """
        UPDATE res_company rc
        SET external_report_layout_id = iuv.id
        FROM ir_ui_view iuv
        WHERE rc.%(external_report_layout)s IS NOT NULL AND
            iuv.name = ('external_layout_' || rc.%(external_report_layout)s)
        """, values)
    cr.execute(
        """
        UPDATE res_company rc
        SET external_report_layout_id = iuv.id
        FROM ir_ui_view iuv
        WHERE rc.%(external_report_layout)s IS NOT NULL
            AND iuv.name = 'external_layout_standard'
            AND external_report_layout_id IS NULL
        """, values)


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    fill_res_company_external_report_layout_id(cr)
