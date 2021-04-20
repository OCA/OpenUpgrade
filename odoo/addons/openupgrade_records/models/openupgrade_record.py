# Copyright 2011-2015 Therp BV <https://therp.nl>
# Copyright 2016-2020 Opener B.V. <https://opener.am>
# Copyright 2019 Eficent <https://eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import ast
import os
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_path, MANIFEST_NAMES


class Attribute(models.Model):
    _name = 'openupgrade.attribute'
    _description = 'OpenUpgrade Attribute'

    name = fields.Char(readonly=True)
    value = fields.Char(readonly=True)
    record_id = fields.Many2one(
        'openupgrade.record', ondelete='CASCADE',
        readonly=True,)


class Record(models.Model):
    _name = 'openupgrade.record'
    _description = 'OpenUpgrade Record'

    name = fields.Char(readonly=True)
    module = fields.Char(readonly=True)
    model = fields.Char(readonly=True)
    field = fields.Char(readonly=True)
    mode = fields.Selection(
            [('create', 'Create'), ('modify', 'Modify')],
            help='Set to Create if a field is newly created '
            'in this module. If this module modifies an attribute of an '
            'existing field, set to Modify.',
            readonly=True)
    type = fields.Selection(  # Uh oh, reserved keyword
            [('field', 'Field'), ('xmlid', 'XML ID'), ('model', 'Model')],
            readonly=True)
    attribute_ids = fields.One2many(
            'openupgrade.attribute', 'record_id',
            readonly=True)
    noupdate = fields.Boolean(readonly=True)
    domain = fields.Char(readonly=True)
    prefix = fields.Char(compute='_compute_prefix_and_suffix')
    suffix = fields.Char(compute='_compute_prefix_and_suffix')
    model_original_module = fields.Char(
        compute='_compute_model_original_module')
    model_type = fields.Char(compute='_compute_model_type')

    @api.depends('name')
    def _compute_prefix_and_suffix(self):
        for rec in self:
            rec.prefix, rec.suffix = rec.name.split('.', 1)

    @api.depends('model', 'type')
    def _compute_model_original_module(self):
        for rec in self:
            if rec.type == 'model':
                rec.model_original_module = \
                    self.env[rec.model]._original_module
            else:
                rec.model_original_module = ''

    @api.depends('model', 'type')
    def _compute_model_type(self):
        for rec in self:
            if rec.type == 'model':
                model = self.env[rec.model]
                if model._auto and model._transient:
                    rec.model_type = 'transient'
                elif model._auto:
                    rec.model_type = ''
                elif not model._auto and model._abstract:
                    rec.model_type = 'abstract'
                else:
                    rec.model_type = 'sql_view'
            else:
                rec.model_type = ''

    @api.model
    def field_dump(self):
        keys = [
            'attachment',
            'module',
            'mode',
            'model',
            'field',
            'type',
            'isfunction',
            'isproperty',
            'isrelated',
            'relation',
            'required',
            'stored',
            'selection_keys',
            'req_default',
            'hasdefault',
            'table',
            'inherits',
            ]

        template = dict([(x, False) for x in keys])
        data = []
        for record in self.search([('type', '=', 'field')]):
            repre = template.copy()
            repre.update({
                'module': record.module,
                'model': record.model,
                'field': record.field,
                'mode': record.mode,
                })
            repre.update(
                dict([(x.name, x.value) for x in record.attribute_ids]))
            data.append(repre)
        return data

    @api.model
    def list_modules(self):
        """ Return the set of covered modules """
        self.env.cr.execute(
            """SELECT DISTINCT(module) FROM openupgrade_record
            ORDER BY module""")
        return [module for module, in self.env.cr.fetchall()]

    @staticmethod
    def _read_manifest(addon_dir):
        for manifest_name in MANIFEST_NAMES:
            if os.access(os.path.join(addon_dir, manifest_name), os.R_OK):
                with open(os.path.join(addon_dir, manifest_name), 'r') as f:
                    manifest_string = f.read()
                    return ast.literal_eval(manifest_string)
        raise ValidationError('No manifest found in %s' % addon_dir)

    @api.model
    def get_xml_records(self, module):
        """ Return all XML records from the given module """
        addon_dir = get_module_path(module)
        manifest = self._read_manifest(addon_dir)
        # The order of the keys are important.
        # Load files in the same order as in
        # module/loading.py:load_module_graph
        files = []
        for key in ['init_xml', 'update_xml', 'data']:
            if not manifest.get(key):
                continue
            for xml_file in manifest[key]:
                if not xml_file.lower().endswith('.xml'):
                    continue
                parts = xml_file.split('/')
                try:
                    with open(os.path.join(addon_dir, *parts), 'r') as xml_handle:
                        files.append(xml_handle.read())
                except UnicodeDecodeError:
                    continue
        return files
