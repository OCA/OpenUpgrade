# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def migrate_auto_confirm(env):
    # Update auto_confirm with old value saved in ir_values
    env.cr.execute("""
        SELECT value
        FROM ir_values
        WHERE model = 'event.config.settings'
        AND name = 'auto_confirmation';
    """)
    value = env.cr.fetchone()
    if value and 'I00' in value[0]:
        openupgrade.logged_query(
            env.cr, """
            UPDATE event_event
            SET auto_confirm = False"""
        )


def migrate_reply_to(env):
    # Convert partner owner of the reply_to email into a follower of event or
    # create a new partner to not lose data
    env.cr.execute("""
        SELECT id, reply_to FROM event_event WHERE reply_to IS NOT NULL;
    """)
    event_rows = env.cr.fetchall()
    for row in event_rows:
        event = env['event.event'].browse(row[0])
        partner = env['res.partner'].search([('email', '=', row[1])])
        if not partner:
            partner = env['res.partner'].create({
                'name': row[1],
                'email': row[1],
            })
        event.message_subscribe(partner_ids=partner[:1].ids)


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.update_module_moved_fields(
        env.cr, 'event.event', ['twitter_hashtag'], 'website_event', 'event')
    migrate_auto_confirm(env)
    migrate_reply_to(env)
    openupgrade.load_data(
        env.cr, 'event', 'migrations/11.0.1.0/noupdate_changes.xml',
    )
