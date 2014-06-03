# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2010 - 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

# This module provides simple tools for OpenUpgrade migration, specific for
# the 7.0 -> 8.0 migration. It is kept in later editions to keep all the API
# docs in the latest release.


def get_last_post_for_model(cr, uid, ids, model_pool):
    """
    Given a set of ids and a model pool, return a dict of each object ids with
    their latest message date as a value.
    To be called in post-migration scripts

    :param cr: database cursor
    :param uid: user id, assumed to be openerp.SUPERUSER_ID
    :param ids: ids of the model in question to retrieve ids
    :param model_pool: orm model pool, assumed to be from pool.get()
    :return: a dict with ids as keys and with dates as values
    """
    if type(ids) is not list:
        ids = [ids]
    res = {}
    for obj in model_pool.browse(cr, uid, ids):
        message_ids = obj.message_ids
        if message_ids:
            res[obj.id] = sorted(
                message_ids, key=lambda x: x.date, reverse=True)[0].date
        else:
            res[obj.id] = False
    return res


def set_message_last_post(cr, uid, pool, models):
    """
    Given a list of models, set their 'message_last_post' fields to an
    estimated last post datetime.
    To be called in post-migration scripts

    :param cr: database cursor
    :param uid: user id, assumed to be openerp.SUPERUSER_ID
    :param pool: orm pool, assumed to be openerp.pooler.get_pool(cr.dbname)
    :param models: a list of model names for which 'message_last_post' needs to \
    be filled
    :return:
    """
    if type(models) is not list:
        models = [models]
    for model in models:
        model_pool = pool[model]
        obj_ids = model_pool.search(cr, uid, [], context={'active_test': False})
        last_posts = get_last_post_for_model(cr, uid, obj_ids, model_pool)
        for i in obj_ids:
            model_pool.write(cr, uid, i, {'message_last_post': last_posts[i]})
