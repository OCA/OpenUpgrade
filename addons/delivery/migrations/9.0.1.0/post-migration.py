# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
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
        "update delivery_price_rule r set carrier_id=g.carrier_id "
        "from delivery_grid g where r.grid_id=g.id")
    cr.execute(
        "insert into delivery_carrier_country_rel (carrier_id, country_id) "
        "select carrier_id, country_id from "
        "delivery_grid_country_rel r join delivery_grid g on r.grid_id=g.id")
    cr.execute(
        "insert into delivery_carrier_state_rel (carrier_id, state_id) "
        "select carrier_id, state_id from "
        "delivery_grid_state_rel r join delivery_grid g on r.grid_id=g.id")
    cr.execute(
        "update delivery_carrier set delivery_type='base_on_rule' "
        "where use_detailed_pricelist")
    cr.execute(
        "update delivery_carrier c set "
        "zip_from=coalesce(c.zip_from, g.zip_from), "
        "zip_to=coalesce(c.zip_to, g.zip_to) "
        "from delivery_grid g where g.carrier_id=c.id")
    rename_property(
        cr, 'res.partner', 'property_delivery_carrier',
        'property_delivery_carrier_id')
