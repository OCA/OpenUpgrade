# -*- coding: utf-8 -*-
# Copyright 2017 bloopark systems (<http://bloopark.de>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


# backup of state column with old / non existing values 'proforma' and
# 'proforma2'
column_copies = {
    'account_invoice ': [
        ('state', None, None),
    ],
}


def add_required_colum_chart_template_id(cr):
    """The model account.reconcile.model.template has now a new required
    many2one field chart_template_id with no default value. To avoid errors
    on module update we add already the column here and fill it with the
    right chart template ID."""
    query = ("ALTER TABLE account_reconcile_model_template "
             "ADD COLUMN chart_template_id integer;")
    openupgrade.logged_query(cr, query)

    cr.execute("""
        SELECT res_id, module FROM ir_model_data
        WHERE model = 'account.reconcile.model.template';
    """)
    rows = cr.fetchall()
    for r in rows:
        cr.execute("""
            SELECT res_id FROM ir_model_data
            WHERE model = 'account.chart.template' AND module = %
            LIMIT 1;
        """, (r[1],))
        chart = cr.fetchone()
        query = ("UPDATE account_reconcile_model_template "
                 "SET chart_template_id = %s "
                 "WHERE id = %s;")
        openupgrade.logged_query(cr, query, (chart[0], r[0]))


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, column_copies)
    add_required_colum_chart_template_id(env.cr)
