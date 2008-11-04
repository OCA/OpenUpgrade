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
import time
import netsvc
from osv import fields, osv
import ir
from mx import DateTime
import tools 
import xmlrpclib
import pooler

from wizard import SERVER,PORT
s = xmlrpclib.Server("http://"+SERVER+":"+str(PORT))

warning_message ="""<?xml version="1.0"?> 
    <form string="!!! Warning"> 
        <image name="gtk-dialog-info" colspan="2"/> 
        <group colspan="2" col="4"> 
            <separator string="%s" colspan="4"/> 
            <label align="0.0" string="%s" colspan="4"/> 
        </group> 
    </form>"""

def get_version(cr, uid,context):
    user = pooler.get_pool(cr.dbname).get('res.users').read(cr,uid,uid,['login'])['login']
    return s.version_list(user)
    
def get_profile(cr,uid,context):
    user = pooler.get_pool(cr.dbname).get('res.users').read(cr,uid,uid,['login'])['login']
    return s.profile_list(user)


def get_language(cr,uid,context,user=None,model=None,lang=None):
    if user:
        if user=='contributor':
            list = s.get_lang_list()
        else:
            login = pooler.get_pool(cr.dbname).get('res.users').read(cr,uid,uid,['login'])['login']
            list = s.get_lang_list(login)
    elif model:
        if model=='ir_translation_contribution':
            sql = "select distinct lang from ir_translation_contribution where state='propose'"
        else:
            sql = "select distinct lang from ir_translation"
        print sql
        cr.execute(sql)
        list = map(lambda x: x[0],cr.fetchall())
        print list
    else :
        sql = "select distinct lang from ir_translation_contribution where state='accept'"
        cr.execute(sql)
        list = map(lambda x: x[0],cr.fetchall())        
    lang_dict = tools.get_languages()
    return [(lang, lang_dict.get(lang, lang)) for lang in list]

class ir_translation_contribution(osv.osv):
    _name = "ir.translation.contribution"
    _inherit = 'ir.translation'
    _description = "Translation Contribution"
    _columns = {
            'contributor_email'  : fields.char('Email Id of Contibutor',size=128),      
            'state': fields.selection(
                    [('draft','Draft'),
                     ('propose','Propose for Change'),
                     ('unchange',"Don't change"),
                     ('accept','Accept'),
                     ('done','Done'),                     
                     ('deny','Deny'),
                     ],
                     'Translation State', readonly=True, select=True),
            'upload':fields.boolean('upload') 
                }
    _sql = ''    

    def write(self, cr, uid, ids, vals, context=None):
        if self.read(cr,uid,ids,['upload']):
            vals['upload']=False
        return super(ir_translation_contribution, self).write(cr, uid, ids, vals, context=context)

ir_translation_contribution()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

