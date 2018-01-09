# coding: utf-8
# Copyright 2017 Odoo Community Association (OCA) <https://odoo-community.org>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models
from openupgradelib import openupgrade, openupgrade_90, openupgrade_tools


def convert_binary_attachment_style(env):
    """ Convert attachment style binary fields """
    field_spec = {}
    for model_name, model in env.items():
        if isinstance(model, models.TransientModel):
            continue
        for k, v in model._fields.items():
            if (v.type == 'binary' and
                    not v.compute and
                    not v.related and
                    not model._fields[k].company_dependent and
                    v.attachment and
                    openupgrade_tools.column_exists(
                        env.cr, model._table, k) and
                    (k, k) not in field_spec.get(model_name, [])):
                field_spec.setdefault(model_name, []).append((k, k))
    if field_spec:
        openupgrade_90.convert_binary_field_to_attachment(env, field_spec)


def compute_store_in_fields(env):
    cr = env.cr
    cr.execute('SELECT id, model, name FROM ir_model_fields WHERE store IS NULL')
    nulls = cr.fetchall()
    for id, modelname, fieldname in nulls:
        model = env.get(modelname, None)
        if model is not None:
            field = model._fields.get(fieldname)
            if field:
                cr.execute(
                    'UPDATE ir_model_fields SET store=%s WHERE id=%s',
                    (field.store, id)
                )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    convert_binary_attachment_style(env)
    compute_store_in_fields(env)
    openupgrade.disable_invalid_filters(env)
