# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 Gábor Dukai
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
{
    "name" : "Unicode Reports with TrueType fonts",
    "version" : "1.1",
    "author" : "Gábor Dukai",
    "website" : "http://exploringopenerp.blogspot.com",
    "description": """
    This module replaces the standard PDF Type1 fonts with TrueType fonts that have
    unicode characters.
    The module contains the DejaVu fonts v2.29 from http://dejavu-fonts.org/
    With this module you can continue to use the old font names in the templates,
    they will be replaced with the DejaVu font names every time before creating a pdf.

    Compatibility: tested with OpenERP v5.0

    NOTE: You have to copy this module to the addons folder. It doesn't work from a zip file!""",
    "depends" : ["base", ],
    "category" : "Generic Modules/Base",
    "demo_xml" : [],
    "update_xml" : [],
    "license": "GPL-3",
    "active": False,
    "installable": True
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

