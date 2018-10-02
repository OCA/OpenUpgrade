# © 2018 Opener B.V. (stefan@opener.amsterdam)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade, openupgrade_merge_records


@openupgrade.migrate()
def migrate(env, version):
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
    env.cr.execute(
        """ UPDATE res_users
            SET active = FALSE, password = NULL WHERE id = %s """,
        (user_root.id,))
