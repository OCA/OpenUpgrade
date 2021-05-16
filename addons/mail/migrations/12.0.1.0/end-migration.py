# Copyright 2018 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
from psycopg2.extensions import AsIs


def fill_mail_tracking_value_track_sequence(env):
    env.cr.execute(
        """
        SELECT DISTINCT mtv.field, mm.model
        FROM mail_tracking_value mtv
        INNER JOIN mail_message mm ON mtv.mail_message_id = mm.id
        INNER JOIN ir_model_fields imf ON (
            imf.name = mtv.field AND mm.model = imf.model)
        WHERE mm.model IS NOT NULL AND imf.track_visibility IS NOT NULL AND
            imf.track_visibility != 'false'
        """
    )
    for field, model in env.cr.fetchall():
        if env.get(model) and field in list(env[model]._fields.keys()):
            sequence = getattr(env[model]._fields[field],
                               'track_sequence', 100)
            if sequence != 100:
                env.cr.execute(
                    """
                    UPDATE mail_tracking_value mtv2
                    SET track_sequence = %s
                    FROM mail_tracking_value mtv
                    INNER JOIN mail_message mm ON mtv.mail_message_id = mm.id
                    WHERE mtv2.id = mtv.id AND mtv.field = %s AND mm.model = %s
                    """ % (sequence, field, model)
                )


def fill_mail_thread_message_main_attachment_id(env):
    thread_models = [k for k in env.registry if issubclass(
        type(env[k]), type(env['mail.thread'])) and env[k]._auto]
    for model in thread_models:
        # the query groups the attachments by their kind of mimetype and
        # res_id. For each res_id, you will have one, two or three of this
        # groups if they exist (and labeled them by 1, 2 or 3), but the query
        # always will select the existing group with the lower label.
        # The max(id) is because the order in attachment model is defined as
        # id DESC.
        openupgrade.logged_query(
            env.cr, """
            UPDATE %s t
            SET message_main_attachment_id = ia.id
            FROM (
                SELECT (array_agg(id))[1] as id, res_id, (array_agg(mt))[1] as mt
                FROM (
                    SELECT max(id) as id, res_id, CASE
                        WHEN mimetype LIKE '%%pdf' THEN 1
                        WHEN mimetype LIKE 'image%%' THEN 2
                        ELSE 3
                    END as mt
                    FROM ir_attachment
                    WHERE res_model = %s
                    GROUP BY res_id, mt
                    ORDER BY res_id, mt) pre_ia
                GROUP BY res_id) ia
            WHERE t.message_main_attachment_id IS NULL
                AND ia.res_id = t.id""",
            (AsIs(env[model]._table), model),
        )


def remove_activity_date_deadline_column(env):
    activity_mixin_models = [k for k in env.registry if issubclass(
        type(env[k]), type(env['mail.activity.mixin'])) and env[k]._auto]
    _column_renames = {
        env[model]._table: [('activity_date_deadline', None)]
        for model in activity_mixin_models if openupgrade.column_exists(
            env.cr, env[model]._table, 'activity_date_deadline')}
    openupgrade.rename_columns(env.cr, _column_renames)


def resubscribe_general_channel(env):
    """After the migration is finished, the general channel is not subscribed
    to itself, so no messages will be received. We are not sure how this
    happens, but the best option is to manually re-subscribe it, as it's
    neutral in case it's already subscribed.
    """
    channel = env.ref("mail.channel_all_employees", False)
    if channel:
        channel.message_subscribe(channel_ids=channel.ids)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    fill_mail_tracking_value_track_sequence(env)
    fill_mail_thread_message_main_attachment_id(env)
    remove_activity_date_deadline_column(env)
    resubscribe_general_channel(env)
