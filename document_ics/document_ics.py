# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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

from osv import osv, fields
from osv.orm import except_orm
import os
import StringIO
import base64
import datetime
import time
import random
import tools

from document import nodes

from tools.safe_eval import safe_eval

ICS_TAGS = {
    'summary':'normal',
    'uid':'normal' ,
    'dtstart':'date' ,
    'dtend':'date' ,
    'created':'date' ,
    'dtstamp':'date' ,
    'last-modified':'normal' ,
    'url':'normal' ,
    'attendee':'multiple',
    'location':'normal',
    'categories': 'normal',
    'description':'normal',

    # TODO: handle the 'duration' property
}

class document_directory_ics_fields(osv.osv):
    _name = 'document.directory.ics.fields'
    _columns = {
        'field_id': fields.many2one('ir.model.fields', 'Open ERP Field', required=True),
        'name': fields.selection(map(lambda x: (x, x), ICS_TAGS.keys()), 'ICS Value', required=True),
        'content_id': fields.many2one('document.directory.content', 'Content', required=True, ondelete='cascade')
    }
document_directory_ics_fields()

class document_directory_content(osv.osv):
    _inherit = 'document.directory.content'
    _columns = {
        'object_id': fields.many2one('ir.model', 'Object', oldname= 'ics_object_id'),
        'obj_iterate': fields.boolean('Iterate object',help="If set, a separate instance will be created for each record of Object"),
        'fname_field': fields.char("Filename field",size=16,help="The field of the object used in the filename. Has to be a unique identifier."),
        'ics_domain': fields.char('Domain', size=64),
        'ics_field_ids': fields.one2many('document.directory.ics.fields', 'content_id', 'Fields Mapping')
    }
    _defaults = {
        'ics_domain': lambda *args: '[]'
    }
    def _file_get(self, cr, node, nodename, content, context=None):
	if not content.obj_iterate:
		return super(document_directory_content, self)._file_get(cr,node,nodename,content)
	else:
		print "iterate over ", content.object_id.model
		mod = self.pool.get(content.object_id.model)
		uid = node.context.uid
		fname_fld = content.fname_field or 'id'
		where = []
		if node.domain:
		    where.append(node.domain)
		if nodename:
		    # Reverse-parse the nodename to deduce the clause:
		    prefix = (content.prefix or '')
		    suffix = (content.suffix or '') + (content.extension or '')
		    if not nodename.startswith(prefix):
			return False
		    if not nodename.endswith(suffix):
			return False
		    tval = nodename[len(prefix):0 - len(suffix)]
		    where.append((fname_fld,'=',tval))
		print "ics iterate clause:", where
		resids = mod.search(cr,uid,where,context=context)
		if not resids:
		    return False
		
		res2 = []
		for ro in mod.read(cr,uid,resids,['id', fname_fld]):
		    print 'ics ro:',ro
		    tname = (content.prefix or '') + str(ro[fname_fld])
		    tname += (content.suffix or '') + (content.extension or '')
		    dctx2 = { 'active_id': ro['id'] }
		    if fname_fld:
			dctx2['active_'+fname_fld] = ro[fname_fld]
		    n = nodes.node_content(tname, node, node.context,content,dctx=dctx2, act_id = ro['id'])
		    n.fill_fields(cr, dctx2)
		    res2.append(n)
		return res2

    def process_write(self, cr, uid, node, data, context=None):
	if node.extension != '.ics':
		return super(document_directory_content).process_write(cr, uid, node, data, context)
        import vobject
        parsedCal = vobject.readOne(data)
        fields = {}
        content = self.browse(cr, uid, node.cnt_id, context)

        idomain = {}
        ctx = (context or {})
        ctx.update(node.context.context.copy())
        ctx.update(node.dctx)
        for d in safe_eval(content.ics_domain,ctx):
	    # TODO: operator?
            idomain[d[0]]=d[2]
        for n in content.ics_field_ids:
            fields[n.name] = n.field_id.name
        if 'uid' not in fields:
            return True
        for child in parsedCal.getChildren():
            result = {}
            uuid = None
            for event in child.getChildren():
                if event.name.lower()=='uid':
                    uuid = event.value
                if event.name.lower() in fields:
                    if ICS_TAGS[event.name.lower()]=='normal':
                        result[fields[event.name.lower()]] = event.value.encode('utf8')
                    elif ICS_TAGS[event.name.lower()]=='date':
                        result[fields[event.name.lower()]] = event.value.strftime('%Y-%m-%d %H:%M:%S')
            if not uuid:
                continue

            fobj = self.pool.get(content.object_id.model)
            id = fobj.search(cr, uid, [(fields['uid'], '=', uuid.encode('utf8'))], context=context)
            if id:
                fobj.write(cr, uid, id, result, context=context)
            else:
                r = idomain.copy()
                r.update(result)
                fobj.create(cr, uid, r, context=context)

        return True

    def process_read(self, cr, uid, node, context=None):
        def ics_datetime(idate, short=False):
            if short:
                return datetime.date.fromtimestamp(time.mktime(time.strptime(idate, '%Y-%m-%d')))
            else:
                return datetime.datetime.strptime(idate, '%Y-%m-%d %H:%M:%S')

	if node.extension != '.ics':
		return super(document_directory_content).process_read(cr, uid, node, context)

        import vobject
        ctx = (context or {})
        ctx.update(node.context.context.copy())
        ctx.update(node.dctx)
        content = self.browse(cr, uid, node.cnt_id, ctx)
        obj_class = self.pool.get(content.object_id.model)

        if content.ics_domain:
            domain = safe_eval(content.ics_domain,ctx)
        else:
            domain = []
        if node.act_id:
            domain.append(('id','=',node.act_id))
        print "process read clause:",domain
        ids = obj_class.search(cr, uid, domain, context=ctx)
        cal = vobject.iCalendar()
        for obj in obj_class.browse(cr, uid, ids):
            event = cal.add('vevent')
            # Fix dtstamp et last-modified with create and write date on the object line
            perm = obj_class.perm_read(cr, uid, [obj.id], context)
            event.add('created').value = ics_datetime(time.strftime('%Y-%m-%d %H:%M:%S'))
            event.add('dtstamp').value = ics_datetime(perm[0]['create_date'][:19])
            if perm[0]['write_date']:
                event.add('last-modified').value = ics_datetime(perm[0]['write_date'][:19])
            for field in content.ics_field_ids:
                value = getattr(obj, field.field_id.name)
                if (not value) and field.name=='uid':
                    value = 'OpenERP-%s_%s@%s' % (content.object_id.model, str(obj.id), cr.dbname,)
                    obj_class.write(cr, uid, [obj.id], {field.field_id.name: value})
                if ICS_TAGS[field.name]=='normal':
                    if type(value)==type(obj):
                        value=value.name
                    value = value or ''
                    event.add(field.name).value = value or ''
                elif ICS_TAGS[field.name]=='date' and value:
                    if field.name == 'dtstart':
                        date_start = start_date = datetime.datetime.fromtimestamp(time.mktime(time.strptime(value , "%Y-%m-%d %H:%M:%S")))
                    if field.name == 'dtend' and isinstance(value, float):
                        value = (start_date + datetime.timedelta(hours=value)).strftime('%Y-%m-%d %H:%M:%S')
                    if len(value)==10:
                        value = ics_datetime(value, True)
                    else:
                        value = ics_datetime(value)
                    event.add(field.name).value = value
        s= cal.serialize()
        cr.commit()
        return s
document_directory_content()

class crm_case(osv.osv):
    _inherit = 'crm.case'
    _columns = {
        'code': fields.char('Calendar Code', size=64),
        'date_deadline': fields.datetime('Deadline', help="Deadline Date is automatically computed from Start Date + Duration"),
    }

    _defaults = {
        'code': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'crm.case'),
    }

    def copy(self, cr, uid, id, default=None, context=None):
        """
        code field must be unique in ICS file
        """
        if not default: default = {}
        if not context: context = {}
        default.update({'code': self.pool.get('ir.sequence').get(cr, uid, 'crm.case'), 'id': False})
        return super(crm_case, self).copy(cr, uid, id, default, context)

    def on_change_duration(self, cr, uid, id, date, duration):
        if not date:
            return {}
        start_date = datetime.datetime.fromtimestamp(time.mktime(time.strptime(date, "%Y-%m-%d %H:%M:%S")))
        if duration >= 0 :
            end = start_date + datetime.timedelta(hours=duration)
        if duration < 0:
            raise osv.except_osv(_('Warning !'),
                    _('You can not set negative Duration.'))

        res = {'value' : {'date_deadline' : end.strftime('%Y-%m-%d %H:%M:%S')}}
        return res

crm_case()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

