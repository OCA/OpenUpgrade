# -*- coding: utf-8 -*-

import os
from osv import osv
import logging

logger = logging.getLogger('OpenUpgrade')
me = os.path.realpath( __file__ )

def migrate(cr, version):
    raise osv.except_osv(
        "OpenUpgrade",
        '%s: You are trying to upgrade the "edi" module, but this module '
        'is new in OpenERP. There was an old '
        'module by the same for communicating with proprietary ERPs. If '
        'you have this module installed, please uninstall and try again. '
        'These modules have nothing in common.' % (me, e)
)
