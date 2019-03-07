# Copyright 2018 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


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
        records = env[model].with_context(active_test=False).search(
            [('message_main_attachment_id', '=', False)])
        attachment_obj = env['ir.attachment'].with_context(
            prefetch_fields=False,
        )
        grouped_attachments = attachment_obj.read_group(
            [('res_model', '=', model)],
            fields=['res_id'],
            groupby=['res_id'])
        attachs = {
            a['res_id']: attachment_obj.search(a['__domain'])
            for a in grouped_attachments
        }
        for record in records:
            all_attachments = attachs.get(record.id, attachment_obj)
            if all_attachments:
                prioritary_attachments = all_attachments.filtered(
                    lambda x: x.mimetype and x.mimetype.endswith('pdf')
                ) or all_attachments.filtered(
                    lambda x: x.mimetype and x.mimetype.startswith('image')
                ) or all_attachments
                record.write({'message_main_attachment_id':
                              prioritary_attachments[0].id})


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    fill_mail_tracking_value_track_sequence(env)
    fill_mail_thread_message_main_attachment_id(env)
