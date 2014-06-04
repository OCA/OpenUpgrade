# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenUpgrade, the free software migration tool for OpenERP
#    Copyright (C) 2014 Akretion (http://www.akretion.com/)
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
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

from openerp.openupgrade import openupgrade
from openerp import pooler, SUPERUSER_ID
import logging

logger = logging.getLogger('OpenUpgrade')


def migrate_filestore(cr, pool):
    cr.execute(
        "SELECT %s, %s FROM document_storage WHERE %s='filestore' "
        "ORDER BY id" % (
            openupgrade.get_legacy_name('name'),
            openupgrade.get_legacy_name('path'),
            openupgrade.get_legacy_name('type'),
            ))
    filestore = cr.fetchall()
    if len(filestore) > 1:
        logger.error(
            "You have several filestore, which is very uncommon. OpenUpgrade "
            "will reconfigure your first filestore (%s), and you will have to "
            "merge the other filestore into your first filestore !"
            % filestore[0][0])

    if filestore:
        logger.info(
            "Migrating the configuration of the filestore '%s' "
            "from document_storage to ir.config_parameter" % filestore[0][0])
        path = filestore[0][1]
        logger.debug("Path of the first filestore = %s" % path)
        pool['ir.config_parameter'].create(
            cr, SUPERUSER_ID, {
                'key': 'ir_attachment.location',
                'value': 'file://%s' % path,
                })
        logger.warning(
            "The new configuration of the filestore suppose that it is now "
            "located at <openerp_server_root>%s. It is not possible to have "
            "an absolute path any more." % path)
        logger.warning(
            "If your filestore is not located at <openerp_server_root>%s, you "
            "should create this directory and move it there, or update "
            "the System Parameter that has the key 'ir_attachment.location'."
            % path)
        logger.info(
            "If you want to know more about the filestore in 7.0, read "
            "the answer from Antony Lesuisse on this question : "
            "https://accounts.openerp.com/fr_FR/forum/Help-1/question/"
            "Where-are-document-Attachments-stored-529")


@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    migrate_filestore(cr, pool)
