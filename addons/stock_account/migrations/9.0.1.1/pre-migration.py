# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def rename_property(cr, model, old_name, new_name):
    # TODO: use openupgradelib's version when #52 is merged
    """Rename property old_name owned by model to new_name. This should happen
    in a pre-migration script."""
    cr.execute(
        "update ir_model_fields f set name=%s "
        "from ir_model m "
        "where m.id=f.model_id and m.model=%s and f.name=%s "
        "returning f.id",
        (new_name, model, old_name))
    field_ids = tuple(i for i, in cr.fetchall())
    cr.execute(
        "update ir_model_data set name=%s where model='ir.model.fields' and "
        "res_id in %s",
        ('%s,%s' % (model, new_name), field_ids))
    cr.execute(
        "update ir_property set name=%s where fields_id in %s",
        (new_name, field_ids))


@openupgrade.migrate()
def migrate(cr, version):
    rename_property(
        cr, 'product.template', 'cost_method', 'property_cost_method')
    rename_property(
        cr, 'product.template', 'valuation', 'property_valuation')
