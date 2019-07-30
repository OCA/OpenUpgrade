# © 2018 Opener B.V. (stefan@opener.amsterdam)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def update_model_terms_translations(env):
    """ Adapt to changes in https://github.com/odoo/odoo/pull/26925, that
    introduces a separate translation type for xml structured fields. First,
    deduplicate existing model translations with new model_terms translations
    that were loaded during the migration. """
    openupgrade.logged_query(
        env.cr, """ DELETE FROM ir_translation WHERE id IN (
        SELECT it2.id FROM ir_translation it1
        JOIN ir_translation it2 ON it1.type in ('model', 'model_terms')
            AND it2.type in ('model', 'model_terms')
            AND it1.name = it2.name
            AND it1.res_id = it2.res_id
            AND it1.lang = it2.lang
            AND it1.id < it2.id); """)
    names = []
    for rec in env['ir.model.fields'].search([('translate', '=', True)]):
        try:
            field = env[rec.model]._fields[rec.name]
        except KeyError:
            continue
        if callable(field.translate):
            names.append('%s,%s' % (rec.model, rec.name))
    if names:
        openupgrade.logged_query(
            env.cr,
            """ UPDATE ir_translation
            SET type = 'model_terms'
            WHERE type = 'model' AND name IN %s """,
            (tuple(names),))


def fill_res_users_password_from_password_crypt(cr):
    openupgrade.logged_query(
        cr,
        """UPDATE res_users
        SET password = password_crypt
        WHERE password_crypt IS NOT NULL
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    update_model_terms_translations(env)
    if openupgrade.column_exists(env.cr, 'res_users', 'password_crypt'):
        fill_res_users_password_from_password_crypt(env.cr)
