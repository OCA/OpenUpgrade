# Copyright 2018 Opener B.V. (stefan@opener.amsterdam)
# Copyright 2018 Paul Catinean <https://github.com/PCatinean>
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.openupgrade_records.lib import apriori
from openupgradelib import openupgrade

model_renames_product = [
    ('product.uom', 'uom.uom'),
    ('product.uom.categ', 'uom.category'),
]

model_renames_stock = [
    ('stock.incoterms', 'account.incoterms'),
]

table_renames_product = [
    ('product_uom', 'uom_uom'),
    ('product_uom_categ', 'uom_category'),
]

table_renames_stock = [
    ('stock_incoterms', 'account_incoterms'),
]

xmlid_renames = [
    ('auth_signup.default_template_user', 'base.template_portal_user_id'),
    ('auth_signup.default_template_user_config',
     'base.default_template_user_config'),
    ('product.group_uom', 'uom.group_uom'),
    ('product.product_uom_gram', 'uom.product_uom_gram'),
    ('product.product_uom_qt', 'uom.product_uom_qt'),
    ('product.product_uom_categ_unit', 'uom.product_uom_categ_unit'),
    ('product.product_uom_categ_kgm', 'uom.product_uom_categ_kgm'),
    ('product.product_uom_categ_vol', 'uom.product_uom_categ_vol'),
    ('product.uom_categ_wtime', 'uom.uom_categ_wtime'),
    ('product.uom_categ_length', 'uom.uom_categ_length'),
    ('product.product_uom_unit', 'uom.product_uom_unit'),
    ('product.product_uom_dozen', 'uom.product_uom_dozen'),
    ('product.product_uom_kgm', 'uom.product_uom_kgm'),
    ('product.product_uom_hour', 'uom.product_uom_hour'),
    ('product.product_uom_day', 'uom.product_uom_day'),
    ('product.product_uom_ton', 'uom.product_uom_ton'),
    ('product.product_uom_meter', 'uom.product_uom_meter'),
    ('product.product_uom_km', 'uom.product_uom_km'),
    ('product.product_uom_litre', 'uom.product_uom_litre'),
    ('product.product_uom_lb', 'uom.product_uom_lb'),
    ('product.product_uom_oz', 'uom.product_uom_oz'),
    ('product.product_uom_cm', 'uom.product_uom_cm'),
    ('product.product_uom_inch', 'uom.product_uom_inch'),
    ('product.product_uom_foot', 'uom.product_uom_foot'),
    ('product.product_uom_mile', 'uom.product_uom_mile'),
    ('product.product_uom_floz', 'uom.product_uom_floz'),
    ('product.product_uom_gal', 'uom.product_uom_gal'),
    ('stock.incoterm_CFR', 'account.incoterm_CFR'),
    ('stock.incoterm_CIF', 'account.incoterm_CIF'),
    ('stock.incoterm_CIP', 'account.incoterm_CIP'),
    ('stock.incoterm_CPT', 'account.incoterm_CPT'),
    ('stock.incoterm_DAF', 'account.incoterm_DAF'),
    ('stock.incoterm_DAP', 'account.incoterm_DAP'),
    ('stock.incoterm_DAT', 'account.incoterm_DAT'),
    ('stock.incoterm_DDP', 'account.incoterm_DDP'),
    ('stock.incoterm_DDU', 'account.incoterm_DDU'),
    ('stock.incoterm_DEQ', 'account.incoterm_DEQ'),
    ('stock.incoterm_DES', 'account.incoterm_DES'),
    ('stock.incoterm_EXW', 'account.incoterm_EXW'),
    ('stock.incoterm_FAS', 'account.incoterm_FAS'),
    ('stock.incoterm_FCA', 'account.incoterm_FCA'),
    ('stock.incoterm_FOB', 'account.incoterm_FOB'),
]


def eliminate_duplicate_translations(cr):
    # Deduplicate code translations
    openupgrade.logged_query(
        cr, """ DELETE FROM ir_translation WHERE id IN (
        SELECT it2.id FROM ir_translation it1
        JOIN ir_translation it2 ON it1.type = 'code'
            AND it1.type = it2.type
            AND it1.src = it2.src
            AND it1.lang = it2.lang
            AND it1.id < it2.id); """)
    # Deduplicate model translations on the same record
    openupgrade.logged_query(
        cr, """ DELETE FROM ir_translation WHERE id IN (
        SELECT it2.id FROM ir_translation it1
        JOIN ir_translation it2 ON it1.type = 'model'
            AND it1.type = it2.type
            AND it1.name = it2.name
            AND it1.res_id = it2.res_id
            AND it1.lang = it2.lang
            AND it1.id < it2.id); """)
    # Deduplicate various
    openupgrade.logged_query(
        cr, """ DELETE FROM ir_translation WHERE id IN (
        SELECT it2.id FROM ir_translation it1
        JOIN ir_translation it2 ON it1.type IN
                ('selection', 'constraint', 'sql_constraint',
                'view', 'field', 'help', 'xsl', 'report')
            AND it1.type = it2.type
            AND it1.name = it2.name
            AND it1.src = it2.src
            AND it1.lang = it2.lang
            AND it1.id < it2.id); """)


def fix_lang_constraints(env):
    """Avoid error on normal update process due to the removal + re-addition of
    constraints.
    """
    openupgrade.logged_query(
        env.cr, """ALTER TABLE ir_translation
        DROP CONSTRAINT ir_translation_lang_fkey_res_lang
        """,
    )


def fix_lang_table(env):
    """Avoid error on normal update process due to changed language codes"""
    openupgrade.logged_query(
        env.cr, "UPDATE res_lang SET code='km_KH' WHERE code='km_KM'"
    )


def fill_ir_ui_view_key(cr):
    openupgrade.logged_query(
        cr,
        """
        UPDATE ir_ui_view
        SET key = COALESCE(split_part(
            arch_fs, '/', 1), 'website') || '.' || replace(
                lower(trim(both from name)), ' ', '_') || '_view'
        WHERE type = 'qweb' AND key IS NULL
        """
    )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    # Deactivate the noupdate flag (hardcoded on initial SQL load) for allowing
    # to update changed data on this group.
    openupgrade.logged_query(
        env.cr, """
        UPDATE ir_model_data SET noupdate=False
        WHERE  module='base' AND name='group_user'""",
    )
    openupgrade.update_module_names(
        env.cr, apriori.renamed_modules.items())
    openupgrade.update_module_names(
        env.cr, apriori.merged_modules.items(), merge_modules=True)
    if openupgrade.table_exists(env.cr, 'product_uom'):
        openupgrade.rename_models(env.cr, model_renames_product)
        openupgrade.rename_tables(env.cr, table_renames_product)
    if openupgrade.table_exists(env.cr, 'stock_incoterms'):
        openupgrade.rename_models(env.cr, model_renames_stock)
        openupgrade.rename_tables(env.cr, table_renames_stock)
    openupgrade.rename_xmlids(env.cr, xmlid_renames)
    eliminate_duplicate_translations(env.cr)

    # Make the system and admin user XML ids refer to the same entry for now to
    # prevent errors when base data is loaded. The users are picked apart in
    # this module's end stage migration script.
    env.cr.execute(
        """ INSERT INTO ir_model_data
        (module, name, model, res_id, noupdate)
        VALUES('base', 'user_admin', 'res.users', 1, true)""")
    env.cr.execute(
        """ INSERT INTO ir_model_data
        (module, name, model, res_id, noupdate)
        (SELECT module, 'partner_admin', model, res_id, noupdate
         FROM ir_model_data WHERE module = 'base' AND name = 'partner_root')
        """)
    fix_lang_constraints(env)
    fix_lang_table(env)
    # for migration of web module
    openupgrade.rename_columns(
        env.cr, {'res_company': [('external_report_layout', None)]})
    # for migration of website module
    fill_ir_ui_view_key(env.cr)
