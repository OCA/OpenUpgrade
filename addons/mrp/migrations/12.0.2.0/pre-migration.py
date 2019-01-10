# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def switch_mrp_xml_id_noupdate(cr):
    """Some references records have an associated XML-ID, that was
    updated in v11 through a method and maintain as XML noupdate=0 data, so
    they weren't removed on updates, but now on v12, that XML-IDs are
    noupdate=1, and no XML data in provided, so on regular update process, they
    are tried to be removed. We switch them to noupdate=1 for avoiding this
    problem.
    """
    openupgrade.logged_query(
        cr, """
        UPDATE ir_model_data
        SET noupdate = True
        WHERE module = 'mrp'
        AND name IN %s""", ((
            'picking_type_manufacturing',
        ), ),
    )


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    switch_mrp_xml_id_noupdate(cr)
