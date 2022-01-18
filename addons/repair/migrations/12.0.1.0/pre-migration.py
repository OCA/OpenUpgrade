# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


_model_renames = [
    ('mrp.repair', 'repair.order'),
    ('mrp.repair.fee', 'repair.fee'),
    ('mrp.repair.line', 'repair.line'),
    ('mrp.repair.cancel', 'repair.cancel'),
    ('mrp.repair.make_invoice', 'repair.order.make_invoice'),
]

_table_renames = [
    ('mrp_repair', 'repair_order'),
    ('mrp_repair_fee', 'repair_fee'),
    ('mrp_repair_line', 'repair_line'),
    ('mrp_repair_cancel', 'repair_cancel'),
    ('mrp_repair_make_invoice', 'repair_order_make_invoice'),
]

xmlid_renames = [
    ('repair.mrp_repair_rule', 'repair.repair_rule'),
    ('repair.seq_mrp_repair', 'repair.seq_repair'),
    ('repair.mail_template_mrp_repair_quotation',
     'repair.mail_template_repair_quotation'),
]


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    openupgrade.rename_models(cr, _model_renames)
    openupgrade.rename_tables(cr, _table_renames)
    openupgrade.rename_xmlids(env.cr, xmlid_renames)
