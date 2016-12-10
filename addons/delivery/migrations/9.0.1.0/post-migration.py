# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def rename_property(cr, model, old_name, new_name):
    """Rename property old_name to new_name. This should happen in a
    pre-migration script."""
    # TODO: propose this to openupgradelib
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
    cr.execute(
        """
        UPDATE delivery_carrier dc
        SET delivery_type='base_on_rule',
            free_if_more_than = old_dc.free_if_more_than,
            fixed_price = old_dc.normal_price
        FROM %s old_dc
        WHERE old_dc.use_detailed_pricelist
            AND old_dc.id = dc.%s
        """ % (
            openupgrade.get_legacy_name('delivery_carrier'),
            openupgrade.get_legacy_name('carrier_id'),
        )
    )
    rename_property(
        cr, 'res.partner', 'property_delivery_carrier',
        'property_delivery_carrier_id',
    )
