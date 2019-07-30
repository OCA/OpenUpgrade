# © 2018 Opener B.V. (stefan@opener.amsterdam)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade, openupgrade_merge_records


def generate_thumbnails(env):
    """ Let Odoo create a thumbnail for all attachments that consist of one of
    the supported image types and are not linked to a binary field. """
    for chunk in openupgrade.chunked(
            env['ir.attachment'].search([
                ('res_field', '=', False),
                ('mimetype', 'like', 'image.%'),
                '|', ('mimetype', 'like', '%gif'),
                '|', ('mimetype', 'like', '%jpeg'),
                '|', ('mimetype', 'like', '%jpg'),
                ('mimetype', 'like', '%png')])):
        for attachment in chunk.with_context(prefetch_fields=False).read(
                ['datas', 'mimetype']):
            res = env['ir.attachment']._make_thumbnail(attachment)
            if res.get('thumbnail'):
                env['ir.attachment'].browse(attachment['id']).write({
                    'thumbnail': res['thumbnail']})


def update_res_company_onboarding_company_state(env):
    # based on old base_onboarding_company_done
    good_companies = env["res.company"].search([]).filtered(lambda c: (
        c.partner_id.browse(
            c.partner_id.sudo().address_get(adr_pref=['contact'])['contact']
        ).sudo().street
    ))
    good_companies.write({'base_onboarding_company_state': 'done'})


def fork_off_system_user(env):
    """ Fork user admin off from user system. User admin keeps the original
    partner, and user system gets a new partner. """
    user_root = env.ref('base.user_root')
    partner_admin = env.ref('base.partner_admin')
    partner_root = env.ref('base.partner_admin').copy({'name': 'System'})
    login = user_root.login
    user_root.login = '__system__'
    user_admin = env.ref('base.user_root').copy({
        'partner_id': partner_admin.id,
        'login': login,
    })
    # copy old passwords for not losing them on new admin user
    crypt = openupgrade.column_exists(env.cr, 'res_users', 'password_crypt')
    set_query = "SET password = ru2.password "
    if crypt:
        set_query += ", password_crypt = ru2.password_crypt "
    env.cr.execute(
        "UPDATE res_users ru " + set_query +
        "FROM res_users ru2 WHERE ru2.id = %s AND ru.id = %s",
        (user_root.id, user_admin.id),
    )
    user_root.write({
        'partner_id': partner_root.id,
        'email': 'root@example.com',
    })
    env.cr.execute(
        """ UPDATE ir_model_data SET res_id = %s
        WHERE module = 'base' AND name = 'user_admin'""", (user_admin.id,))
    env.cr.execute(
        """ UPDATE ir_model_data SET res_id = %s
        WHERE module = 'base' AND name = 'partner_root'""", (partner_root.id,))
    openupgrade.logged_query(
        env.cr,
        """ UPDATE ir_model_data SET res_id = %(user_admin)s
        WHERE model = 'res.users' AND res_id = %(user_root)s
        AND (module != 'base' OR name != 'user_root') """,
        {'user_admin': user_admin.id, 'user_root': user_root.id})
    # Get create_uid and write_uid columns to ignore
    env.cr.execute(
        """ SELECT tc.table_name, kcu.column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE constraint_type = 'FOREIGN KEY'
            AND ccu.table_name = 'res_users' and ccu.column_name = 'id'
            AND kcu.column_name IN ('create_uid', 'write_uid')
        """)
    exclude_columns = env.cr.fetchall() + [
        ('ir_cron', 'user_id'), ('res_groups_users_rel', 'uid'),
        ('res_company_users_rel', 'user_id'),
    ]

    openupgrade_merge_records.merge_records(
        env, 'res.users', [user_root.id], user_admin.id,
        method='sql', delete=False, exclude_columns=exclude_columns)
    # Circumvent ORM when setting root user inactive, because
    # "You cannot deactivate the user you're currently logged in as."
    set_query = "SET active = FALSE, password = NULL"
    if crypt:
        set_query += ", password_crypt = NULL"
    env.cr.execute(
        "UPDATE res_users " + set_query + " WHERE id = %s",
        (user_root.id, ),
    )
    # Ensure also partner_root is inactive
    env.cr.execute(
        """ UPDATE res_partner
            SET active = FALSE WHERE id = %s """,
        (partner_root.id,))


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    env['ir.ui.menu']._parent_store_compute()
    env['res.partner.category']._parent_store_compute()
    generate_thumbnails(env)
    update_res_company_onboarding_company_state(env)
    openupgrade.load_data(
        env.cr, 'base', 'migrations/12.0.1.3/noupdate_changes.xml')
    # Activate back the noupdate flag on the group
    openupgrade.logged_query(
        env.cr, """
        UPDATE ir_model_data SET noupdate=True
        WHERE  module='base' AND name='group_user'""",
    )
    fork_off_system_user(env)
