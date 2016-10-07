# coding: utf-8
# Copyright 2011-2015 Therp BV <https://therp.nl>
# Copyright 2016 Opener B.V. <https://opener.am>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
This module can be used to contain functions that should be called at the end
of the migration. A migration may be run several times after corrections in
the code or the configuration, and there is no way for OpenERP to detect a
succesful result. Therefore, the functions in this module should be robust
against being run multiple times on the same database.
"""
import logging
logger = logging.getLogger('OpenUpgrade.deferred')


def migrate_deferred(cr, pool):
    logger.info('Deferred migration step called')
