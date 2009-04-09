# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import os

PATH = "/tmp"
SERVER = ""
PORT = 8000

contrib = os.path.join(PATH, "translation","contrib")
publish = os.path.join(PATH,"translation","publish")

user_info={
    'admin':'admin',
    'dhara':'dhara'
}
list_lang={
    'zh_CN': ['admin'],
    'zh_TW': ['admin'],
    'cs_CZ': ['admin'],
    'de_DE': ['admin'],
    'es_AR': ['admin','dhara'],
    'es_ES': ['admin','dhara'],
    'fr_FR': ['admin','dhara'],
    'fr_CH': ['admin','dhara'],
    'en_EN': ['admin','dhara'],
    'hu_HU': ['dhara'],
    'it_IT': ['dhara'],
    'pt_BR': ['dhara','admin'],
    'pt_PT': ['dhara'],
    'nl_NL': ['dhara'],
    'ro_RO': [],
    'ru_RU': [],
    'sv_SE': [],
    'fr_BE': ['admin','dhara'],
    'fr_XX': ['admin','dhara'],
}
dependent_language = {
    'fr_FR' : ['fr_BE','fr_XX']
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

