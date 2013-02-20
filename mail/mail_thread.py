# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2009-today OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

import base64
import datetime
import dateutil
import email
import logging
import pytz
import re
import time
import xmlrpclib
from email.message import Message

from openerp import tools
from openerp import SUPERUSER_ID
from openerp.addons.mail.mail_message import decode
from openerp.osv import fields, osv
from openerp.tools.safe_eval import safe_eval as eval

_logger = logging.getLogger(__name__)


def decode_header(message, header, separator=' '):
    return separator.join(map(decode, filter(None, message.get_all(header, []))))


class mail_thread(osv.AbstractModel):
    ''' mail_thread model is meant to be inherited by any model that needs to
        act as a discussion topic on which messages can be attached. Public
        methods are prefixed with ``message_`` in order to avoid name
        collisions with methods of the models that will inherit from this class.

        ``mail.thread`` defines fields used to handle and display the
        communication history. ``mail.thread`` also manages followers of
        inheriting classes. All features and expected behavior are managed
        by mail.thread. Widgets has been designed for the 7.0 and following
        versions of OpenERP.

        Inheriting classes are not required to implement any method, as the
        default implementation will work for any model. However it is common
        to override at least the ``message_new`` and ``message_update``
        methods (calling ``super``) to add model-specific behavior at
        creation and update of a thread when processing incoming emails.

        Options:
            - _mail_flat_thread: if set to True, all messages without parent_id
                are automatically attached to the first message posted on the
                ressource. If set to False, the display of Chatter is done using
                threads, and no parent_id is automatically set.
    '''
    _name = 'mail.thread'
    _description = 'Email Thread'
    _mail_flat_thread = True

    # Automatic logging system if mail installed
    # _track = {
    #   'field': {
    #       'module.subtype_xml': lambda self, cr, uid, obj, context=None: obj[state] == done,
    #       'module.subtype_xml2': lambda self, cr, uid, obj, context=None: obj[state] != done,
    #   },
    #   'field2': {
    #       ...
    #   },
    # }
    # where
    #   :param string field: field name
    #   :param module.subtype_xml: xml_id of a mail.message.subtype (i.e. mail.mt_comment)
    #   :param obj: is a browse_record
    #   :param function lambda: returns whether the tracking should record using this subtype
    _track = {}

    def _get_message_data(self, cr, uid, ids, name, args, context=None):
        """ Computes:
            - message_unread: has uid unread message for the document
            - message_summary: html snippet summarizing the Chatter for kanban views """
        res = dict((id, dict(message_unread=False, message_summary='')) for id in ids)
        user_pid = self.pool.get('res.users').read(cr, uid, uid, ['partner_id'], context=context)['partner_id'][0]

        # search for unread messages, directly in SQL to improve performances
        cr.execute("""  SELECT m.res_id FROM mail_message m
                        RIGHT JOIN mail_notification n
                        ON (n.message_id = m.id AND n.partner_id = %s AND (n.read = False or n.read IS NULL))
                        WHERE m.model = %s AND m.res_id in %s""",
                    (user_pid, self._name, tuple(ids),))
        msg_ids = [result[0] for result in cr.fetchall()]
        for msg_id in msg_ids:
            res[msg_id]['message_unread'] = True

        for thread in self.browse(cr, uid, ids, context=context):
            cls = res[thread.id]['message_unread'] and ' class="oe_kanban_mail_new"' or ''
            res[thread.id]['message_summary'] = "<span%s><span class='oe_e'>9</span> %d</span> <span><span class='oe_e'>+</span> %d</span>" % (cls, len(thread.message_ids), len(thread.message_follower_ids))

        return res

    def _get_subscription_data(self, cr, uid, ids, name, args, context=None):
        """ Computes:
            - message_subtype_data: data about document subtypes: which are
                available, which are followed if any """
        res = dict((id, dict(message_subtype_data='')) for id in ids)
        user_pid = self.pool.get('res.users').read(cr, uid, uid, ['partner_id'], context=context)['partner_id'][0]

        # find current model subtypes, add them to a dictionary
        subtype_obj = self.pool.get('mail.message.subtype')
        subtype_ids = subtype_obj.search(cr, uid, ['|', ('res_model', '=', self._name), ('res_model', '=', False)], context=context)
        subtype_dict = dict((subtype.name, dict(default=subtype.default, followed=False, id=subtype.id)) for subtype in subtype_obj.browse(cr, uid, subtype_ids, context=context))
        for id in ids:
            res[id]['message_subtype_data'] = subtype_dict.copy()

        # find the document followers, update the data
        fol_obj = self.pool.get('mail.followers')
        fol_ids = fol_obj.search(cr, uid, [
            ('partner_id', '=', user_pid),
            ('res_id', 'in', ids),
            ('res_model', '=', self._name),
        ], context=context)
        for fol in fol_obj.browse(cr, uid, fol_ids, context=context):
            thread_subtype_dict = res[fol.res_id]['message_subtype_data']
            for subtype in fol.subtype_ids:
                thread_subtype_dict[subtype.name]['followed'] = True
            res[fol.res_id]['message_subtype_data'] = thread_subtype_dict

        return res

    def _search_message_unread(self, cr, uid, obj=None, name=None, domain=None, context=None):
        return [('message_ids.to_read', '=', True)]

    def _get_followers(self, cr, uid, ids, name, arg, context=None):
        fol_obj = self.pool.get('mail.followers')
        fol_ids = fol_obj.search(cr, SUPERUSER_ID, [('res_model', '=', self._name), ('res_id', 'in', ids)])
        res = dict((id, dict(message_follower_ids=[], message_is_follower=False)) for id in ids)
        user_pid = self.pool.get('res.users').read(cr, uid, uid, ['partner_id'], context=context)['partner_id'][0]
        for fol in fol_obj.browse(cr, SUPERUSER_ID, fol_ids):
            res[fol.res_id]['message_follower_ids'].append(fol.partner_id.id)
            if fol.partner_id.id == user_pid:
                res[fol.res_id]['message_is_follower'] = True
        return res

    def _set_followers(self, cr, uid, id, name, value, arg, context=None):
        if not value:
            return
        partner_obj = self.pool.get('res.partner')
        fol_obj = self.pool.get('mail.followers')

        # read the old set of followers, and determine the new set of followers
        fol_ids = fol_obj.search(cr, SUPERUSER_ID, [('res_model', '=', self._name), ('res_id', '=', id)])
        old = set(fol.partner_id.id for fol in fol_obj.browse(cr, SUPERUSER_ID, fol_ids))
        new = set(old)

        for command in value or []:
            if isinstance(command, (int, long)):
                new.add(command)
            elif command[0] == 0:
                new.add(partner_obj.create(cr, uid, command[2], context=context))
            elif command[0] == 1:
                partner_obj.write(cr, uid, [command[1]], command[2], context=context)
                new.add(command[1])
            elif command[0] == 2:
                partner_obj.unlink(cr, uid, [command[1]], context=context)
                new.discard(command[1])
            elif command[0] == 3:
                new.discard(command[1])
            elif command[0] == 4:
                new.add(command[1])
            elif command[0] == 5:
                new.clear()
            elif command[0] == 6:
                new = set(command[2])

        # remove partners that are no longer followers
        fol_ids = fol_obj.search(cr, SUPERUSER_ID,
            [('res_model', '=', self._name), ('res_id', '=', id), ('partner_id', 'not in', list(new))])
        fol_obj.unlink(cr, SUPERUSER_ID, fol_ids)

        # add new followers
        for partner_id in new - old:
            fol_obj.create(cr, SUPERUSER_ID, {'res_model': self._name, 'res_id': id, 'partner_id': partner_id})

    def _search_followers(self, cr, uid, obj, name, args, context):
        fol_obj = self.pool.get('mail.followers')
        res = []
        for field, operator, value in args:
            assert field == name
            fol_ids = fol_obj.search(cr, SUPERUSER_ID, [('res_model', '=', self._name), ('partner_id', operator, value)])
            res_ids = [fol.res_id for fol in fol_obj.browse(cr, SUPERUSER_ID, fol_ids)]
            res.append(('id', 'in', res_ids))
        return res

    _columns = {
        'message_is_follower': fields.function(_get_followers,
            type='boolean', string='Is a Follower', multi='_get_followers,'),
        'message_follower_ids': fields.function(_get_followers, fnct_inv=_set_followers,
                fnct_search=_search_followers, type='many2many',
                obj='res.partner', string='Followers', multi='_get_followers'),
        'message_ids': fields.one2many('mail.message', 'res_id',
            domain=lambda self: [('model', '=', self._name)],
            auto_join=True,
            string='Messages',
            help="Messages and communication history"),
        'message_unread': fields.function(_get_message_data,
            fnct_search=_search_message_unread, multi="_get_message_data",
            type='boolean', string='Unread Messages',
            help="If checked new messages require your attention."),
        'message_summary': fields.function(_get_message_data, method=True,
            type='text', string='Summary', multi="_get_message_data",
            help="Holds the Chatter summary (number of messages, ...). "\
                 "This summary is directly in html format in order to "\
                 "be inserted in kanban views."),
    }

    #------------------------------------------------------
    # CRUD overrides for automatic subscription and logging
    #------------------------------------------------------

    def create(self, cr, uid, values, context=None):
        """ Chatter override :
            - subscribe uid
            - subscribe followers of parent
            - log a creation message
        """
        if context is None:
            context = {}
        thread_id = super(mail_thread, self).create(cr, uid, values, context=context)

        # subscribe uid unless asked not to
        if not context.get('mail_create_nosubscribe'):
            self.message_subscribe_users(cr, uid, [thread_id], [uid], context=context)
        self.message_auto_subscribe(cr, uid, [thread_id], values.keys(), context=context)

        # automatic logging unless asked not to (mainly for various testing purpose)
        if not context.get('mail_create_nolog'):
            self.message_post(cr, uid, thread_id, body='Document created', context=context)
        return thread_id

    def write(self, cr, uid, ids, values, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        # Track initial values of tracked fields
        tracked_fields = self._get_tracked_fields(cr, uid, values.keys(), context=context)
        if tracked_fields:
            initial = self.read(cr, uid, ids, tracked_fields.keys(), context=context)
            initial_values = dict((item['id'], item) for item in initial)

        # Perform write, update followers
        result = super(mail_thread, self).write(cr, uid, ids, values, context=context)
        self.message_auto_subscribe(cr, uid, ids, values.keys(), context=context)

        # Perform the tracking
        if tracked_fields:
            self.message_track(cr, uid, ids, tracked_fields, initial_values, context=context)
        return result

    def unlink(self, cr, uid, ids, context=None):
        """ Override unlink to delete messages and followers. This cannot be
            cascaded, because link is done through (res_model, res_id). """
        msg_obj = self.pool.get('mail.message')
        fol_obj = self.pool.get('mail.followers')
        # delete messages and notifications
        msg_ids = msg_obj.search(cr, uid, [('model', '=', self._name), ('res_id', 'in', ids)], context=context)
        msg_obj.unlink(cr, uid, msg_ids, context=context)
        # delete
        res = super(mail_thread, self).unlink(cr, uid, ids, context=context)
        # delete followers
        fol_ids = fol_obj.search(cr, SUPERUSER_ID, [('res_model', '=', self._name), ('res_id', 'in', ids)], context=context)
        fol_obj.unlink(cr, SUPERUSER_ID, fol_ids, context=context)
        return res

    def copy(self, cr, uid, id, default=None, context=None):
        default = default or {}
        default['message_ids'] = []
        default['message_follower_ids'] = []
        return super(mail_thread, self).copy(cr, uid, id, default=default, context=context)

    #------------------------------------------------------
    # Automatically log tracked fields
    #------------------------------------------------------

    def _get_tracked_fields(self, cr, uid, updated_fields, context=None):
        """ Return a structure of tracked fields for the current model.
            :param list updated_fields: modified field names
            :return list: a list of (field_name, column_info obj), containing
                always tracked fields and modified on_change fields
        """
        lst = []
        for name, column_info in self._all_columns.items():
            visibility = getattr(column_info.column, 'track_visibility', False)
            if visibility == 'always' or (visibility == 'onchange' and name in updated_fields) or name in self._track:
                lst.append(name)
        if not lst:
            return lst
        return self.fields_get(cr, uid, lst, context=context)

    def message_track(self, cr, uid, ids, tracked_fields, initial_values, context=None):

        def convert_for_display(value, col_info):
            if not value and col_info['type'] == 'boolean':
                return 'False'
            if not value:
                return ''
            if col_info['type'] == 'many2one':
                return value[1]
            if col_info['type'] == 'selection':
                return dict(col_info['selection'])[value]
            return value

        def format_message(message_description, tracked_values):
            message = ''
            if message_description:
                message = '<span>%s</span>' % message_description
            for name, change in tracked_values.items():
                message += '<div> &nbsp; &nbsp; &bull; <b>%s</b>: ' % change.get('col_info')
                if change.get('old_value'):
                    message += '%s &rarr; ' % change.get('old_value')
                message += '%s</div>' % change.get('new_value')
            return message

        if not tracked_fields:
            return True

        for record in self.read(cr, uid, ids, tracked_fields.keys(), context=context):
            initial = initial_values[record['id']]
            changes = []
            tracked_values = {}

            # generate tracked_values data structure: {'col_name': {col_info, new_value, old_value}}
            for col_name, col_info in tracked_fields.items():
                if record[col_name] == initial[col_name] and getattr(self._all_columns[col_name].column, 'track_visibility', None) == 'always':
                    tracked_values[col_name] = dict(col_info=col_info['string'],
                                                        new_value=convert_for_display(record[col_name], col_info))
                elif record[col_name] != initial[col_name]:
                    if getattr(self._all_columns[col_name].column, 'track_visibility', None) in ['always', 'onchange']:
                        tracked_values[col_name] = dict(col_info=col_info['string'],
                                                            old_value=convert_for_display(initial[col_name], col_info),
                                                            new_value=convert_for_display(record[col_name], col_info))
                    if col_name in tracked_fields:
                        changes.append(col_name)
            if not changes:
                continue

            # find subtypes and post messages or log if no subtype found
            subtypes = []
            for field, track_info in self._track.items():
                if field not in changes:
                    continue
                for subtype, method in track_info.items():
                    if method(self, cr, uid, record, context):
                        subtypes.append(subtype)

            posted = False
            for subtype in subtypes:
                try:
                    subtype_rec = self.pool.get('ir.model.data').get_object(cr, uid, subtype.split('.')[0], subtype.split('.')[1])
                except ValueError, e:
                    _logger.debug('subtype %s not found, giving error "%s"' % (subtype, e))
                    continue
                message = format_message(subtype_rec.description if subtype_rec.description else subtype_rec.name, tracked_values)
                self.message_post(cr, uid, record['id'], body=message, subtype=subtype, context=context)
                posted = True
            if not posted:
                message = format_message('', tracked_values)
                self.message_post(cr, uid, record['id'], body=message, context=context)
        return True

    #------------------------------------------------------
    # mail.message wrappers and tools
    #------------------------------------------------------

    def _needaction_domain_get(self, cr, uid, context=None):
        if self._needaction:
            return [('message_unread', '=', True)]
        return []

    #------------------------------------------------------
    # Email specific
    #------------------------------------------------------

    def message_get_reply_to(self, cr, uid, ids, context=None):
        if not self._inherits.get('mail.alias'):
            return [False for id in ids]
        return ["%s@%s" % (record['alias_name'], record['alias_domain'])
                    if record.get('alias_domain') and record.get('alias_name')
                    else False
                    for record in self.read(cr, uid, ids, ['alias_name', 'alias_domain'], context=context)]

    #------------------------------------------------------
    # Mail gateway
    #------------------------------------------------------

    def message_capable_models(self, cr, uid, context=None):
        """ Used by the plugin addon, based for plugin_outlook and others. """
        ret_dict = {}
        for model_name in self.pool.obj_list():
            model = self.pool.get(model_name)
            if 'mail.thread' in getattr(model, '_inherit', []):
                ret_dict[model_name] = model._description
        return ret_dict

    def _message_find_partners(self, cr, uid, message, header_fields=['From'], context=None):
        """ Find partners related to some header fields of the message. """
        s = ', '.join([decode(message.get(h)) for h in header_fields if message.get(h)])
        return [partner_id for email in tools.email_split(s)
                for partner_id in self.pool.get('res.partner').search(cr, uid, [('email', 'ilike', email)], limit=1, context=context)]

    def _message_find_user_id(self, cr, uid, message, context=None):
        from_local_part = tools.email_split(decode(message.get('From')))[0]
        # FP Note: canonification required, the minimu: .lower()
        user_ids = self.pool.get('res.users').search(cr, uid, ['|',
            ('login', '=', from_local_part),
            ('email', '=', from_local_part)], context=context)
        return user_ids[0] if user_ids else uid

    def message_route(self, cr, uid, message, model=None, thread_id=None,
                      custom_values=None, context=None):
        """Attempt to figure out the correct target model, thread_id,
        custom_values and user_id to use for an incoming message.
        Multiple values may be returned, if a message had multiple
        recipients matching existing mail.aliases, for example.

        The following heuristics are used, in this order:
             1. If the message replies to an existing thread_id, and
                properly contains the thread model in the 'In-Reply-To'
                header, use this model/thread_id pair, and ignore
                custom_value (not needed as no creation will take place)
             2. Look for a mail.alias entry matching the message
                recipient, and use the corresponding model, thread_id,
                custom_values and user_id.
             3. Fallback to the ``model``, ``thread_id`` and ``custom_values``
                provided.
             4. If all the above fails, raise an exception.

           :param string message: an email.message instance
           :param string model: the fallback model to use if the message
               does not match any of the currently configured mail aliases
               (may be None if a matching alias is supposed to be present)
           :type dict custom_values: optional dictionary of default field values
                to pass to ``message_new`` if a new record needs to be created.
                Ignored if the thread record already exists, and also if a
                matching mail.alias was found (aliases define their own defaults)
           :param int thread_id: optional ID of the record/thread from ``model``
               to which this mail should be attached. Only used if the message
               does not reply to an existing thread and does not match any mail alias.
           :return: list of [model, thread_id, custom_values, user_id]
        """
        assert isinstance(message, Message), 'message must be an email.message.Message at this point'
        message_id = message.get('Message-Id')
        references = decode_header(message, 'References')
        in_reply_to = decode_header(message, 'In-Reply-To')

        # 1. Verify if this is a reply to an existing thread
        thread_references = references or in_reply_to
        ref_match = thread_references and tools.reference_re.search(thread_references)
        if ref_match:
            thread_id = int(ref_match.group(1))
            model = ref_match.group(2) or model
            model_pool = self.pool.get(model)
            if thread_id and model and model_pool and model_pool.exists(cr, uid, thread_id) \
                and hasattr(model_pool, 'message_update'):
                _logger.debug('Routing mail with Message-Id %s: direct reply to model: %s, thread_id: %s, custom_values: %s, uid: %s',
                              message_id, model, thread_id, custom_values, uid)
                return [(model, thread_id, custom_values, uid)]

        # Verify whether this is a reply to a private message
        if in_reply_to:
            message_ids = self.pool.get('mail.message').search(cr, uid, [('message_id', '=', in_reply_to)], limit=1, context=context)
            if message_ids:
                message = self.pool.get('mail.message').browse(cr, uid, message_ids[0], context=context)
                _logger.debug('Routing mail with Message-Id %s: direct reply to a private message: %s, custom_values: %s, uid: %s',
                                message_id, message.id, custom_values, uid)
                return [(message.model, message.res_id, custom_values, uid)]

        # 2. Look for a matching mail.alias entry
        # Delivered-To is a safe bet in most modern MTAs, but we have to fallback on To + Cc values
        # for all the odd MTAs out there, as there is no standard header for the envelope's `rcpt_to` value.
        rcpt_tos = \
             ','.join([decode_header(message, 'Delivered-To'),
                       decode_header(message, 'To'),
                       decode_header(message, 'Cc'),
                       decode_header(message, 'Resent-To'),
                       decode_header(message, 'Resent-Cc')])
        local_parts = [e.split('@')[0] for e in tools.email_split(rcpt_tos)]
        if local_parts:
            mail_alias = self.pool.get('mail.alias')
            alias_ids = mail_alias.search(cr, uid, [('alias_name', 'in', local_parts)])
            if alias_ids:
                routes = []
                for alias in mail_alias.browse(cr, uid, alias_ids, context=context):
                    user_id = alias.alias_user_id.id
                    if not user_id:
                        # TDE note: this could cause crashes, because no clue that the user
                        # that send the email has the right to create or modify a new document
                        # Fallback on user_id = uid
                        # Note: recognized partners will be added as followers anyway
                        # user_id = self._message_find_user_id(cr, uid, message, context=context)
                        user_id = uid
                        _logger.debug('No matching user_id for the alias %s', alias.alias_name)
                    routes.append((alias.alias_model_id.model, alias.alias_force_thread_id, \
                                   eval(alias.alias_defaults), user_id))
                _logger.debug('Routing mail with Message-Id %s: direct alias match: %r', message_id, routes)
                return routes

        # 3. Fallback to the provided parameters, if they work
        model_pool = self.pool.get(model)
        if not thread_id:
            # Legacy: fallback to matching [ID] in the Subject
            match = tools.res_re.search(decode_header(message, 'Subject'))
            thread_id = match and match.group(1)
        assert thread_id and hasattr(model_pool, 'message_update') or hasattr(model_pool, 'message_new'), \
            "No possible route found for incoming message with Message-Id %s. " \
            "Create an appropriate mail.alias or force the destination model." % message_id
        if thread_id and not model_pool.exists(cr, uid, thread_id):
            _logger.warning('Received mail reply to missing document %s! Ignoring and creating new document instead for Message-Id %s',
                            thread_id, message_id)
            thread_id = None
        _logger.debug('Routing mail with Message-Id %s: fallback to model:%s, thread_id:%s, custom_values:%s, uid:%s',
                      message_id, model, thread_id, custom_values, uid)
        return [(model, thread_id, custom_values, uid)]

    def message_process(self, cr, uid, model, message, custom_values=None,
                        save_original=False, strip_attachments=False,
                        thread_id=None, context=None):
        """ Process an incoming RFC2822 email message, relying on
            ``mail.message.parse()`` for the parsing operation,
            and ``message_route()`` to figure out the target model.

            Once the target model is known, its ``message_new`` method
            is called with the new message (if the thread record did not exist)
            or its ``message_update`` method (if it did).

            There is a special case where the target model is False: a reply
            to a private message. In this case, we skip the message_new /
            message_update step, to just post a new message using mail_thread
            message_post.

           :param string model: the fallback model to use if the message
               does not match any of the currently configured mail aliases
               (may be None if a matching alias is supposed to be present)
           :param message: source of the RFC2822 message
           :type message: string or xmlrpclib.Binary
           :type dict custom_values: optional dictionary of field values
                to pass to ``message_new`` if a new record needs to be created.
                Ignored if the thread record already exists, and also if a
                matching mail.alias was found (aliases define their own defaults)
           :param bool save_original: whether to keep a copy of the original
                email source attached to the message after it is imported.
           :param bool strip_attachments: whether to strip all attachments
                before processing the message, in order to save some space.
           :param int thread_id: optional ID of the record/thread from ``model``
               to which this mail should be attached. When provided, this
               overrides the automatic detection based on the message
               headers.
        """
        if context is None:
            context = {}

        # extract message bytes - we are forced to pass the message as binary because
        # we don't know its encoding until we parse its headers and hence can't
        # convert it to utf-8 for transport between the mailgate script and here.
        if isinstance(message, xmlrpclib.Binary):
            message = str(message.data)
        # Warning: message_from_string doesn't always work correctly on unicode,
        # we must use utf-8 strings here :-(
        if isinstance(message, unicode):
            message = message.encode('utf-8')
        msg_txt = email.message_from_string(message)
        routes = self.message_route(cr, uid, msg_txt, model,
                                    thread_id, custom_values,
                                    context=context)
        msg = self.message_parse(cr, uid, msg_txt, save_original=save_original, context=context)
        if strip_attachments:
            msg.pop('attachments', None)

        # postpone setting msg.partner_ids after message_post, to avoid double notifications
        partner_ids = msg.pop('partner_ids', [])

        thread_id = False
        for model, thread_id, custom_values, user_id in routes:
            if self._name == 'mail.thread':
                context.update({'thread_model': model})
            if model:
                model_pool = self.pool.get(model)
                assert thread_id and hasattr(model_pool, 'message_update') or hasattr(model_pool, 'message_new'), \
                    "Undeliverable mail with Message-Id %s, model %s does not accept incoming emails" % \
                        (msg['message_id'], model)

                # disabled subscriptions during message_new/update to avoid having the system user running the
                # email gateway become a follower of all inbound messages
                nosub_ctx = dict(context, mail_create_nosubscribe=True)
                if thread_id and hasattr(model_pool, 'message_update'):
                    model_pool.message_update(cr, user_id, [thread_id], msg, context=nosub_ctx)
                else:
                    thread_id = model_pool.message_new(cr, user_id, msg, custom_values, context=nosub_ctx)
            else:
                assert thread_id == 0, "Posting a message without model should be with a null res_id, to create a private message."
                model_pool = self.pool.get('mail.thread')
            new_msg_id = model_pool.message_post_user_api(cr, uid, [thread_id], context=context, content_subtype='html', **msg)

            # when posting an incoming email to a document: subscribe the author, if a partner, as follower
            if model and thread_id and msg.get('author_id'):
                model_pool.message_subscribe(cr, uid, [thread_id], [msg.get('author_id')], context=context)

            if partner_ids:
                # postponed after message_post, because this is an external message and we don't want to create
                # duplicate emails due to notifications
                self.pool.get('mail.message').write(cr, uid, [new_msg_id], {'partner_ids': partner_ids}, context=context)

        return thread_id

    def message_new(self, cr, uid, msg_dict, custom_values=None, context=None):
        """Called by ``message_process`` when a new message is received
           for a given thread model, if the message did not belong to
           an existing thread.
           The default behavior is to create a new record of the corresponding
           model (based on some very basic info extracted from the message).
           Additional behavior may be implemented by overriding this method.

           :param dict msg_dict: a map containing the email details and
                                 attachments. See ``message_process`` and
                                ``mail.message.parse`` for details.
           :param dict custom_values: optional dictionary of additional
                                      field values to pass to create()
                                      when creating the new thread record.
                                      Be careful, these values may override
                                      any other values coming from the message.
           :param dict context: if a ``thread_model`` value is present
                                in the context, its value will be used
                                to determine the model of the record
                                to create (instead of the current model).
           :rtype: int
           :return: the id of the newly created thread object
        """
        if context is None:
            context = {}
        data = {}
        if isinstance(custom_values, dict):
            data = custom_values.copy()
        model = context.get('thread_model') or self._name
        model_pool = self.pool.get(model)
        fields = model_pool.fields_get(cr, uid, context=context)
        if 'name' in fields and not data.get('name'):
            data['name'] = msg_dict.get('subject', '')
        res_id = model_pool.create(cr, uid, data, context=context)
        return res_id

    def message_update(self, cr, uid, ids, msg_dict, update_vals=None, context=None):
        """Called by ``message_process`` when a new message is received
           for an existing thread. The default behavior is to update the record
           with update_vals taken from the incoming email.
           Additional behavior may be implemented by overriding this
           method.
           :param dict msg_dict: a map containing the email details and
                               attachments. See ``message_process`` and
                               ``mail.message.parse()`` for details.
           :param dict update_vals: a dict containing values to update records
                              given their ids; if the dict is None or is
                              void, no write operation is performed.
        """
        if update_vals:
            self.write(cr, uid, ids, update_vals, context=context)
        return True

    def _message_extract_payload(self, message, save_original=False):
        """Extract body as HTML and attachments from the mail message"""
        attachments = []
        body = u''
        if save_original:
            attachments.append(('original_email.eml', message.as_string()))
        if not message.is_multipart() or 'text/' in message.get('content-type', ''):
            encoding = message.get_content_charset()
            body = message.get_payload(decode=True)
            body = tools.ustr(body, encoding, errors='replace')
            if message.get_content_type() == 'text/plain':
                # text/plain -> <pre/>
                body = tools.append_content_to_html(u'', body, preserve=True)
        else:
            alternative = (message.get_content_type() == 'multipart/alternative')
            for part in message.walk():
                if part.get_content_maintype() == 'multipart':
                    continue  # skip container
                filename = part.get_filename()  # None if normal part
                encoding = part.get_content_charset()  # None if attachment
                # 1) Explicit Attachments -> attachments
                if filename or part.get('content-disposition', '').strip().startswith('attachment'):
                    attachments.append((filename or 'attachment', part.get_payload(decode=True)))
                    continue
                # 2) text/plain -> <pre/>
                if part.get_content_type() == 'text/plain' and (not alternative or not body):
                    body = tools.append_content_to_html(body, tools.ustr(part.get_payload(decode=True),
                                                                         encoding, errors='replace'), preserve=True)
                # 3) text/html -> raw
                elif part.get_content_type() == 'text/html':
                    html = tools.ustr(part.get_payload(decode=True), encoding, errors='replace')
                    if alternative:
                        body = html
                    else:
                        body = tools.append_content_to_html(body, html, plaintext=False)
                # 4) Anything else -> attachment
                else:
                    attachments.append((filename or 'attachment', part.get_payload(decode=True)))
        return body, attachments

    def message_parse(self, cr, uid, message, save_original=False, context=None):
        """Parses a string or email.message.Message representing an
           RFC-2822 email, and returns a generic dict holding the
           message details.

           :param message: the message to parse
           :type message: email.message.Message | string | unicode
           :param bool save_original: whether the returned dict
               should include an ``original`` attachment containing
               the source of the message
           :rtype: dict
           :return: A dict with the following structure, where each
                    field may not be present if missing in original
                    message::

                    { 'message_id': msg_id,
                      'subject': subject,
                      'from': from,
                      'to': to,
                      'cc': cc,
                      'body': unified_body,
                      'attachments': [('file1', 'bytes'),
                                      ('file2', 'bytes')}
                    }
        """
        msg_dict = {
            'type': 'email',
            'author_id': False,
        }
        if not isinstance(message, Message):
            if isinstance(message, unicode):
                # Warning: message_from_string doesn't always work correctly on unicode,
                # we must use utf-8 strings here :-(
                message = message.encode('utf-8')
            message = email.message_from_string(message)

        message_id = message['message-id']
        if not message_id:
            # Very unusual situation, be we should be fault-tolerant here
            message_id = "<%s@localhost>" % time.time()
            _logger.debug('Parsing Message without message-id, generating a random one: %s', message_id)
        msg_dict['message_id'] = message_id

        if 'Subject' in message:
            msg_dict['subject'] = decode(message.get('Subject'))

        # Envelope fields not stored in mail.message but made available for message_new()
        msg_dict['from'] = decode(message.get('from'))
        msg_dict['to'] = decode(message.get('to'))
        msg_dict['cc'] = decode(message.get('cc'))

        if 'From' in message:
            author_ids = self._message_find_partners(cr, uid, message, ['From'], context=context)
            if author_ids:
                msg_dict['author_id'] = author_ids[0]
            else:
                msg_dict['email_from'] = decode(message.get('from'))
        partner_ids = self._message_find_partners(cr, uid, message, ['To', 'Cc'], context=context)
        msg_dict['partner_ids'] = [(4, partner_id) for partner_id in partner_ids]

        if 'Date' in message:
            try:
                date_hdr = decode(message.get('Date'))
                parsed_date = dateutil.parser.parse(date_hdr, fuzzy=True)
                if parsed_date.utcoffset() is None:
                    # naive datetime, so we arbitrarily decide to make it
                    # UTC, there's no better choice. Should not happen,
                    # as RFC2822 requires timezone offset in Date headers.
                    stored_date = parsed_date.replace(tzinfo=pytz.utc)
                else:
                    stored_date = parsed_date.astimezone(pytz.utc)
            except Exception:
                _logger.warning('Failed to parse Date header %r in incoming mail '
                                'with message-id %r, assuming current date/time.',
                                message.get('Date'), message_id)
                stored_date = datetime.datetime.now()
            msg_dict['date'] = stored_date.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)

        if 'In-Reply-To' in message:
            parent_ids = self.pool.get('mail.message').search(cr, uid, [('message_id', '=', decode(message['In-Reply-To']))])
            if parent_ids:
                msg_dict['parent_id'] = parent_ids[0]

        if 'References' in message and 'parent_id' not in msg_dict:
            parent_ids = self.pool.get('mail.message').search(cr, uid, [('message_id', 'in',
                                                                         [x.strip() for x in decode(message['References']).split()])])
            if parent_ids:
                msg_dict['parent_id'] = parent_ids[0]

        msg_dict['body'], msg_dict['attachments'] = self._message_extract_payload(message)
        return msg_dict

    #------------------------------------------------------
    # Note specific
    #------------------------------------------------------

    def log(self, cr, uid, id, message, secondary=False, context=None):
        _logger.warning("log() is deprecated. As this module inherit from "\
                        "mail.thread, the message will be managed by this "\
                        "module instead of by the res.log mechanism. Please "\
                        "use mail_thread.message_post() instead of the "\
                        "now deprecated res.log.")
        self.message_post(cr, uid, [id], message, context=context)

    def message_create_partners_from_emails(self, cr, uid, emails, context=None):
        """ Convert a list of emails into a list partner_ids and a list
            new_partner_ids. The return value is non conventional because
            it is meant to be used by the mail widget.

            :return dict: partner_ids and new_partner_ids
        """
        partner_obj = self.pool.get('res.partner')
        mail_message_obj = self.pool.get('mail.message')

        partner_ids = []
        new_partner_ids = []
        for email in emails:
            m = re.search(r"((.+?)\s*<)?([^<>]+@[^<>]+)>?", email, re.IGNORECASE | re.DOTALL)
            name = m.group(2) or m.group(0)
            email = m.group(3)
            ids = partner_obj.search(cr, SUPERUSER_ID, [('email', '=', email)], context=context)
            if ids:
                partner_ids.append(ids[0])
                partner_id = ids[0]
            else:
                partner_id = partner_obj.create(cr, uid, {
                        'name': name or email,
                        'email': email,
                    }, context=context)
                new_partner_ids.append(partner_id)

            # link mail with this from mail to the new partner id
            message_ids = mail_message_obj.search(cr, SUPERUSER_ID, ['|', ('email_from', '=', email), ('email_from', 'ilike', '<%s>' % email), ('author_id', '=', False)], context=context)
            if message_ids:
                mail_message_obj.write(cr, SUPERUSER_ID, message_ids, {'email_from': None, 'author_id': partner_id}, context=context)
        return {
            'partner_ids': partner_ids,
            'new_partner_ids': new_partner_ids,
        }

    def message_post(self, cr, uid, thread_id, body='', subject=None, type='notification',
                        subtype=None, parent_id=False, attachments=None, context=None, **kwargs):
        """ Post a new message in an existing thread, returning the new
            mail.message ID. Extra keyword arguments will be used as default
            column values for the new mail.message record.
            Auto link messages for same id and object
            :param int thread_id: thread ID to post into, or list with one ID;
                if False/0, mail.message model will also be set as False
            :param str body: body of the message, usually raw HTML that will
                be sanitized
            :param str subject: optional subject
            :param str type: mail_message.type
            :param int parent_id: optional ID of parent message in this thread
            :param tuple(str,str) attachments or list id: list of attachment tuples in the form
                ``(name,content)``, where content is NOT base64 encoded
            :return: ID of newly created mail.message
        """
        if context is None:
            context = {}
        if attachments is None:
            attachments = {}

        assert (not thread_id) or isinstance(thread_id, (int, long)) or \
            (isinstance(thread_id, (list, tuple)) and len(thread_id) == 1), "Invalid thread_id; should be 0, False, an ID or a list with one ID"
        if isinstance(thread_id, (list, tuple)):
            thread_id = thread_id and thread_id[0]
        mail_message = self.pool.get('mail.message')

        # if we're processing a message directly coming from the gateway, the destination model was
        # set in the context. 
        model = False
        if thread_id:
            model = context.get('thread_model', self._name) if self._name == 'mail.thread' else self._name

        attachment_ids = kwargs.pop('attachment_ids', [])
        for name, content in attachments:
            if isinstance(content, unicode):
                content = content.encode('utf-8')
            data_attach = {
                'name': name,
                'datas': base64.b64encode(str(content)),
                'datas_fname': name,
                'description': name,
                'res_model': context.get('thread_model') or self._name,
                'res_id': thread_id,
            }
            attachment_ids.append((0, 0, data_attach))

        # fetch subtype
        if subtype:
            s_data = subtype.split('.')
            if len(s_data) == 1:
                s_data = ('mail', s_data[0])
            ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, s_data[0], s_data[1])
            subtype_id = ref and ref[1] or False
        else:
            subtype_id = False

        # _mail_flat_thread: automatically set free messages to the first posted message
        if self._mail_flat_thread and not parent_id and thread_id:
            message_ids = mail_message.search(cr, uid, ['&', ('res_id', '=', thread_id), ('model', '=', model)], context=context, order="id ASC", limit=1)
            parent_id = message_ids and message_ids[0] or False
        # we want to set a parent: force to set the parent_id to the oldest ancestor, to avoid having more than 1 level of thread
        elif parent_id:
            message_ids = mail_message.search(cr, SUPERUSER_ID, [('id', '=', parent_id), ('parent_id', '!=', False)], context=context)
            # avoid loops when finding ancestors
            processed_list = []
            if message_ids:
                message = mail_message.browse(cr, SUPERUSER_ID, message_ids[0], context=context)
                while (message.parent_id and message.parent_id.id not in processed_list):
                    processed_list.append(message.parent_id.id)
                    message = message.parent_id
                parent_id = message.id

        values = kwargs
        values.update({
            'model': model,
            'res_id': thread_id or False,
            'body': body,
            'subject': subject or False,
            'type': type,
            'parent_id': parent_id,
            'attachment_ids': attachment_ids,
            'subtype_id': subtype_id,
        })

        # Avoid warnings about non-existing fields
        for x in ('from', 'to', 'cc'):
            values.pop(x, None)

        return mail_message.create(cr, uid, values, context=context)

    def message_post_user_api(self, cr, uid, thread_id, body='', parent_id=False,
                                attachment_ids=None, content_subtype='plaintext',
                                context=None, **kwargs):
        """ Wrapper on message_post, used for user input :
            - mail gateway
            - quick reply in Chatter (refer to mail.js), not
                the mail.compose.message wizard
            The purpose is to perform some pre- and post-processing:
            - if body is plaintext: convert it into html
            - if parent_id: handle reply to a previous message by adding the
                parent partners to the message
            - type and subtype: comment and mail.mt_comment by default
            - attachment_ids: supposed not attached to any document; attach them
                to the related document. Should only be set by Chatter.
        """
        mail_message_obj = self.pool.get('mail.message')
        ir_attachment = self.pool.get('ir.attachment')

        # 1.A.1: add recipients of parent message (# TDE FIXME HACK: mail.thread -> private message)
        partner_ids = set([])
        if parent_id and self._name == 'mail.thread':
            parent_message = mail_message_obj.browse(cr, uid, parent_id, context=context)
            partner_ids |= set([(4, partner.id) for partner in parent_message.partner_ids])
            if parent_message.author_id.id:
                partner_ids.add((4, parent_message.author_id.id))

        # 1.A.2: add specified recipients
        param_partner_ids = set()
        for item in kwargs.pop('partner_ids', []):
            if isinstance(item, (list)):
                param_partner_ids.add((item[0], item[1]))
            elif isinstance(item, (int, long)):
                param_partner_ids.add((4, item))
            else:
                param_partner_ids.add(item)
        partner_ids |= param_partner_ids

        # 1.A.3: add parameters recipients as follower
        # TDE FIXME in 7.1: should check whether this comes from email_list or partner_ids
        if param_partner_ids and self._name != 'mail.thread':
            self.message_subscribe(cr, uid, [thread_id], [pid[1] for pid in param_partner_ids], context=context)

        # 1.B: handle body, message_type and message_subtype
        if content_subtype == 'plaintext':
            body = tools.plaintext2html(body)
        msg_type = kwargs.pop('type', 'comment')
        msg_subtype = kwargs.pop('subtype', 'mail.mt_comment')

        # 2. Pre-processing: attachments
        # HACK TDE FIXME: Chatter: attachments linked to the document (not done JS-side), load the message
        if attachment_ids:
            # TDE FIXME (?): when posting a private message, we use mail.thread as a model
            # However, attaching doc to mail.thread is not possible, mail.thread does not have any table
            model = self._name
            if model == 'mail.thread':
                model = False
            filtered_attachment_ids = ir_attachment.search(cr, SUPERUSER_ID, [
                ('res_model', '=', 'mail.compose.message'),
                ('res_id', '=', 0),
                ('create_uid', '=', uid),
                ('id', 'in', attachment_ids)], context=context)
            if filtered_attachment_ids:
                if thread_id and model:
                    ir_attachment.write(cr, SUPERUSER_ID, attachment_ids, {'res_model': model, 'res_id': thread_id}, context=context)
        else:
            attachment_ids = []
        attachment_ids = [(4, id) for id in attachment_ids]

        # 3. Post message
        return self.message_post(cr, uid, thread_id=thread_id, body=body,
                            type=msg_type, subtype=msg_subtype, parent_id=parent_id,
                            attachment_ids=attachment_ids, partner_ids=list(partner_ids), context=context, **kwargs)

    #------------------------------------------------------
    # Followers API
    #------------------------------------------------------

    def message_get_subscription_data(self, cr, uid, ids, context=None):
        """ Wrapper to get subtypes data. """
        return self._get_subscription_data(cr, uid, ids, None, None, context=context)

    def message_subscribe_users(self, cr, uid, ids, user_ids=None, subtype_ids=None, context=None):
        """ Wrapper on message_subscribe, using users. If user_ids is not
            provided, subscribe uid instead. """
        if user_ids is None:
            user_ids = [uid]
        partner_ids = [user.partner_id.id for user in self.pool.get('res.users').browse(cr, uid, user_ids, context=context)]
        return self.message_subscribe(cr, uid, ids, partner_ids, subtype_ids=subtype_ids, context=context)

    def message_subscribe(self, cr, uid, ids, partner_ids, subtype_ids=None, context=None):
        """ Add partners to the records followers. """
        user_pid = self.pool.get('res.users').read(cr, uid, uid, ['partner_id'], context=context)['partner_id'][0]
        if set(partner_ids) == set([user_pid]):
            self.check_access_rights(cr, uid, 'read')
        else:
            self.check_access_rights(cr, uid, 'write')

        self.write(cr, SUPERUSER_ID, ids, {'message_follower_ids': [(4, pid) for pid in partner_ids]}, context=context)
        # if subtypes are not specified (and not set to a void list), fetch default ones
        if subtype_ids is None:
            subtype_obj = self.pool.get('mail.message.subtype')
            subtype_ids = subtype_obj.search(cr, uid, [('default', '=', True), '|', ('res_model', '=', self._name), ('res_model', '=', False)], context=context)
        # update the subscriptions
        fol_obj = self.pool.get('mail.followers')
        fol_ids = fol_obj.search(cr, SUPERUSER_ID, [('res_model', '=', self._name), ('res_id', 'in', ids), ('partner_id', 'in', partner_ids)], context=context)
        fol_obj.write(cr, SUPERUSER_ID, fol_ids, {'subtype_ids': [(6, 0, subtype_ids)]}, context=context)
        return True

    def message_unsubscribe_users(self, cr, uid, ids, user_ids=None, context=None):
        """ Wrapper on message_subscribe, using users. If user_ids is not
            provided, unsubscribe uid instead. """
        if user_ids is None:
            user_ids = [uid]
        partner_ids = [user.partner_id.id for user in self.pool.get('res.users').browse(cr, uid, user_ids, context=context)]
        return self.message_unsubscribe(cr, uid, ids, partner_ids, context=context)

    def message_unsubscribe(self, cr, uid, ids, partner_ids, context=None):
        """ Remove partners from the records followers. """
        user_pid = self.pool.get('res.users').read(cr, uid, uid, ['partner_id'], context=context)['partner_id'][0]
        if set(partner_ids) == set([user_pid]):
            self.check_access_rights(cr, uid, 'read')
        else:
            self.check_access_rights(cr, uid, 'write')
        return self.write(cr, SUPERUSER_ID, ids, {'message_follower_ids': [(3, pid) for pid in partner_ids]}, context=context)

    def _message_get_auto_subscribe_fields(self, cr, uid, updated_fields, auto_follow_fields=['user_id'], context=None):
        """ Returns the list of relational fields linking to res.users that should
            trigger an auto subscribe. The default list checks for the fields
            - called 'user_id'
            - linking to res.users
            - with track_visibility set
            In OpenERP V7, this is sufficent for all major addon such as opportunity,
            project, issue, recruitment, sale.
            Override this method if a custom behavior is needed about fields
            that automatically subscribe users.
        """
        user_field_lst = []
        for name, column_info in self._all_columns.items():
            if name in auto_follow_fields and name in updated_fields and getattr(column_info.column, 'track_visibility', False) and column_info.column._obj == 'res.users':
                user_field_lst.append(name)
        return user_field_lst

    def message_auto_subscribe(self, cr, uid, ids, updated_fields, context=None):
        """
            1. fetch project subtype related to task (parent_id.res_model = 'project.task')
            2. for each project subtype: subscribe the follower to the task
        """
        subtype_obj = self.pool.get('mail.message.subtype')
        follower_obj = self.pool.get('mail.followers')

        # fetch auto_follow_fields
        user_field_lst = self._message_get_auto_subscribe_fields(cr, uid, updated_fields, context=context)

        # fetch related record subtypes
        related_subtype_ids = subtype_obj.search(cr, uid, ['|', ('res_model', '=', False), ('parent_id.res_model', '=', self._name)], context=context)
        subtypes = subtype_obj.browse(cr, uid, related_subtype_ids, context=context)
        default_subtypes = [subtype for subtype in subtypes if subtype.res_model == False]
        related_subtypes = [subtype for subtype in subtypes if subtype.res_model != False]
        relation_fields = set([subtype.relation_field for subtype in subtypes if subtype.relation_field != False])
        if (not related_subtypes or not any(relation in updated_fields for relation in relation_fields)) and not user_field_lst:
            return True

        for record in self.browse(cr, uid, ids, context=context):
            new_followers = dict()
            parent_res_id = False
            parent_model = False
            for subtype in related_subtypes:
                if not subtype.relation_field or not subtype.parent_id:
                    continue
                if not subtype.relation_field in self._columns or not getattr(record, subtype.relation_field, False):
                    continue
                parent_res_id = getattr(record, subtype.relation_field).id
                parent_model = subtype.res_model
                follower_ids = follower_obj.search(cr, SUPERUSER_ID, [
                    ('res_model', '=', parent_model),
                    ('res_id', '=', parent_res_id),
                    ('subtype_ids', 'in', [subtype.id])
                    ], context=context)
                for follower in follower_obj.browse(cr, SUPERUSER_ID, follower_ids, context=context):
                    new_followers.setdefault(follower.partner_id.id, set()).add(subtype.parent_id.id)

            if parent_res_id and parent_model:
                for subtype in default_subtypes:
                    follower_ids = follower_obj.search(cr, SUPERUSER_ID, [
                        ('res_model', '=', parent_model),
                        ('res_id', '=', parent_res_id),
                        ('subtype_ids', 'in', [subtype.id])
                        ], context=context)
                    for follower in follower_obj.browse(cr, SUPERUSER_ID, follower_ids, context=context):
                        new_followers.setdefault(follower.partner_id.id, set()).add(subtype.id)

            # add followers coming from res.users relational fields that are tracked
            user_ids = [getattr(record, name).id for name in user_field_lst if getattr(record, name)]
            for partner_id in [user.partner_id.id for user in self.pool.get('res.users').browse(cr, SUPERUSER_ID, user_ids, context=context)]:
                new_followers.setdefault(partner_id, None)

            for pid, subtypes in new_followers.items():
                subtypes = list(subtypes) if subtypes is not None else None
                self.message_subscribe(cr, uid, [record.id], [pid], subtypes, context=context)
        return True

    #------------------------------------------------------
    # Thread state
    #------------------------------------------------------

    def message_mark_as_unread(self, cr, uid, ids, context=None):
        """ Set as unread. """
        partner_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).partner_id.id
        cr.execute('''
            UPDATE mail_notification SET
                read=false
            WHERE
                message_id IN (SELECT id from mail_message where res_id=any(%s) and model=%s limit 1) and
                partner_id = %s
        ''', (ids, self._name, partner_id))
        return True

    def message_mark_as_read(self, cr, uid, ids, context=None):
        """ Set as read. """
        partner_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).partner_id.id
        cr.execute('''
            UPDATE mail_notification SET
                read=true
            WHERE
                message_id IN (SELECT id FROM mail_message WHERE res_id=ANY(%s) AND model=%s) AND
                partner_id = %s
        ''', (ids, self._name, partner_id))
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
