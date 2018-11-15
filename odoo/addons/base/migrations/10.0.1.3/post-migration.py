# coding: utf-8
# © 2017-2018 Opener BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import csv
from openupgradelib import openupgrade, openupgrade_merge_records
from odoo.modules.module import get_module_resource


def handle_im_odoo_support_views(env):
    """ im_odoo_support is a deprecated module, merged into im_livechat.
    If the latter module is not installed, a broken version of
    im_odoo_support.assets_backend is left in the database which breaks the
    web client after the migration. """
    module = env['ir.module.module'].search([('name', '=', 'im_livechat')])
    if module and module.state not in ('to upgrade', 'installed'):
        view = env.ref('im_livechat.assets_backend', False)
        if view and not env['ir.ui.view'].search([
                ('inherit_id', '=', view.id)]):
            view.unlink()


def clean_states_with_no_code(env):
    """This method ensures that if you have countries
    introduced manually without code, then merge them with the same countries
    but with coded ones"""
    country_model = env['res.country']
    wrong_countries = country_model.search([('code', '=', False)])
    for wrong_country in wrong_countries:
        good_country = country_model.search(
            [('name', 'in',
              [
                  wrong_country.name.strip(),
                  wrong_country.name.strip().title(),
              ]),
             ('code', '!=', False),
             ])
        if good_country:
            openupgrade_merge_records.merge_records(
                env, 'res.country',
                wrong_country.ids,
                good_country.id,
                {
                    'address_format': 'other',
                    'phone_code': 'min',
                    'country_group_ids': 'merge',
                    'state_ids': 'merge',
                }
            )


def merge_country_states(env):
    """"You may have duplicated countries states,
    so ensure you merge the duplicated ones"""
    clean_states_with_no_code(env)
    group_list = [
        'country_id', 'code',
    ]
    country_state_model = env['res.country.state']
    groups = country_state_model.read_group(
        [], group_list, group_list, lazy=False,
    )
    for group in groups:
        country_states = country_state_model.search(group['__domain'])
        if len(country_states) == 1:
            continue
        correct_country_states = country_states.filtered(
            lambda cs: cs.country_id.address_format)
        if correct_country_states:
            openupgrade_merge_records.merge_records(
                env, 'res.country.state',
                (country_states - correct_country_states[-1]).ids,
                correct_country_states[-1].id,
            )
        else:
            openupgrade_merge_records.merge_records(
                env, 'res.country.state',
                (country_states - country_states[-1]).ids,
                country_states[-1].id,
            )
    # Use here same method as pre-migration method, partially, just in case:
    with open(get_module_resource('base', 'res', 'res.country.state.csv'),
              'rb') as country_states_file:
        states = csv.reader(country_states_file, delimiter=',', quotechar='"')
        for row, state in enumerate(states):
            if row == 0:
                continue
            data_name = state[0]
            country_code = state[1]
            name = state[2]
            state_code = state[3]
            env.cr.execute(
                """
                SELECT imd.id
                FROM ir_model_data imd
                INNER JOIN res_country_state rcs ON (
                    imd.model = 'res.country.state' AND imd.res_id = rcs.id)
                LEFT JOIN res_country rc ON rcs.country_id = rc.id
                INNER JOIN ir_model_data imd2 ON (
                    rc.id = imd2.res_id AND imd2.model = 'res.country')
                WHERE imd2.name = '%(country_code)s'
                    AND rcs.code = '%(state_code)s'
                ORDER BY imd.id DESC
                LIMIT 1
                """ % {
                    'country_code': country_code,
                    'state_code': state_code,
                }
            )
            found_id = env.cr.fetchone()
            if not found_id:
                continue
            openupgrade.logged_query(
                env.cr,
                """
                UPDATE ir_model_data
                SET name = '%(data_name)s', module = 'base'
                WHERE id = %(data_id)s AND model = 'res.country.state'
                """ % {
                    'data_name': data_name,
                    'data_id': found_id[0],
                }
            )
            env.cr.execute(
                """
                UPDATE res_country_state rcs
                SET name = $$%(name)s$$
                FROM ir_model_data imd
                WHERE imd.id = %(data_id)s
                    AND imd.model = 'res.country.state'
                    AND imd.res_id = rcs.id
                """ % {
                    'name': name,
                    'data_id': found_id[0],
                }
            )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    handle_im_odoo_support_views(env)
    merge_country_states(env)
    openupgrade.load_data(
        env.cr, 'base', 'migrations/10.0.1.3/noupdate_changes.xml'
    )
