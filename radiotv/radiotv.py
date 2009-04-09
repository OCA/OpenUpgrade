# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                    Jordi Esteve <jesteve@zikzakmedia.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import osv, fields
import time
import xmlrpclib
import wizard.export_table


def day_week(self, last=0, nweek=0):
    # Computes the first day (last=0) of the current week (nweek=0) or the last day (last=1) of the current week (nweek=0). It is added nweek weeks from the current week (nweek can be negative)
    import datetime
    day = datetime.date.today()
    wd = day.weekday()
    if not last:
        offset = datetime.timedelta(days = -wd + nweek*7)
        day = day + offset
        print "%04i-%02i-%02i 00:00:00" % (day.year, day.month, day.day)
        return "%04i-%02i-%02i 00:00:00" % (day.year, day.month, day.day)
    else:
        offset = datetime.timedelta(days = -wd + nweek*7 + 6)
        day = day + offset
        print "%04i-%02i-%02i 23:59:59" % (day.year, day.month, day.day)
        return "%04i-%02i-%02i 23:59:59" % (day.year, day.month, day.day)


def get_server(self, cr, uid):
    # Gets the website server to synchronize
    rtv_web = self.pool.get('radiotv.web')
    web_ids = rtv_web.search(cr, uid, [('active','=',True),('sync','=',True)])
    websites = rtv_web.browse(cr, uid, web_ids)
    if websites:
        server = xmlrpclib.ServerProxy(websites[0].url + "/tinyerp-synchro.php")
    else:
        server = False
    return server
    

class radiotv_program(osv.osv):
    _name = 'radiotv.program'
radiotv_program()

class radiotv_category(osv.osv):
    _name = 'radiotv.category'
radiotv_category()

class radiotv_broadcast(osv.osv):
    _name = 'radiotv.broadcast'
radiotv_broadcast()


class radiotv_channel(osv.osv):
    _name = 'radiotv.channel'
    _columns = {
        'name': fields.char('Name', size=200, required=True),
        'description': fields.text('Description'),
        'program_ids': fields.many2many(
            'radiotv.program',
            'radiotv_channel_program_rel',
            'channel_id',
            'program_id',
            'Programs'),
    }
    _order = 'name'

    def write(self, cr, uid, ids, vals, context=None):
        if not context:
            context={}
        #print "write:", ids, vals
        result = super(radiotv_channel, self).write(cr, uid, ids, vals, context=context)

        # Synchronize to website
        server = get_server(self, cr, uid)
        if callable(server):
            (new, update) = wizard.export_table.export_write(self, cr, uid, server, 'channel', ids, vals, context)
        return result


    def create(self, cr, uid, vals, context=None):
        if not context:
            context={}
        #print "create:", vals
        id = super(radiotv_channel, self).create(cr, uid, vals, context=context)

        # Synchronize to website
        server = get_server(self, cr, uid)
        if callable(server):
            (new, update) = wizard.export_table.export_write(self, cr, uid, server, 'channel', [id], vals, context)
        return id


    def unlink(self, cr, uid, ids):
        #print "ulink:", ids
        result = super(radiotv_channel, self).unlink(cr, uid, ids)

        # Synchronize to website
        server = get_server(self, cr, uid)
        if callable(server):
            delete = wizard.export_table.export_ulink(self, cr, uid, server, 'channel', ids, "channel_program_rel", "channel_id")
        return result
radiotv_channel()


class radiotv_program(osv.osv):
    _name = 'radiotv.program'
    _columns = {
        'name': fields.char('Name', size=200, required=True),
        'introduction': fields.text('Introduction', required=True),
        'description': fields.text('Description'),
        'state': fields.selection([('-1','Archive'),('0','Unpublish'),('1','Publish')], 'State', required=True),
        'email': fields.char('Email', size=100),
        'editor': fields.char('Editor', size=100),
        'team': fields.text('Team'),
        'channel_ids': fields.many2many(
            'radiotv.channel',
            'radiotv_channel_program_rel',
            'program_id',
            'channel_id',
            'Channels'),
        'category_id': fields.many2one('radiotv.category', 'Category'),
        #'broadcast_ids': fields.one2many('radiotv.broadcast', 'program_id', 'Broadcasts'),
        'original_language': fields.char('Original language', size=50),
        'broadcast_language': fields.char('Broadcast language', size=50),
        'production_country_id': fields.many2one('res.country', 'Production country'),
        'production_year': fields.integer('Production year', size=4),
        'production_type': fields.selection([('0','Own'),('1','Foreign')], 'Production type', required=True),
        'classification': fields.selection([('0','For everybody'),('1','Especially recommended for the children'),('2','Not recommended for minors of 7'),('3','Not recommended for minors of 13'),('4','Not recommended for minors of 18')], 'Classification', required=True),
        'approx_duration': fields.integer('Approx. duration', size=4, help='Approximate duration in minutes'),
    }
    _defaults = {
        'state': lambda *a: '1',
        'email': lambda *a: '@rtvvilafranca.cat',
    }
    _order = 'name'


    def write(self, cr, uid, ids, vals, context=None):
        if not context:
            context={}
        #print "write:", ids, vals
        result = super(radiotv_program, self).write(cr, uid, ids, vals, context=context)

        # Synchronize to website
        server = get_server(self, cr, uid)
        if callable(server):
            (new, update) = wizard.export_table.export_write(self, cr, uid, server, 'program', ids, vals, context)
        return result


    def create(self, cr, uid, vals, context=None):
        if not context:
            context={}
        #print "create:", vals
        id = super(radiotv_program, self).create(cr, uid, vals, context=context)

        # Synchronize to website
        server = get_server(self, cr, uid)
        if callable(server):
            (new, update) = wizard.export_table.export_write(self, cr, uid, server, 'program', [id], vals, context)
        return id


    def unlink(self, cr, uid, ids):
        #print "ulink:", ids
        result = super(radiotv_program, self).unlink(cr, uid, ids)

        # Synchronize to website
        server = get_server(self, cr, uid)
        if callable(server):
            delete = wizard.export_table.export_ulink(self, cr, uid, server, 'program', ids, "channel_program_rel", "program_id")
        return result
radiotv_program()


class radiotv_category(osv.osv):
    _name = 'radiotv.category'
    _columns = {
        'name': fields.char('Name', size=200, required=True),
        'description': fields.text('Description'),
        'program_ids': fields.one2many('radiotv.program', 'category_id', 'Programs'),
    }
    _order = 'name'


    def write(self, cr, uid, ids, vals, context=None):
        if not context:
            context={}
        #print "write:", ids, vals
        result = super(radiotv_category, self).write(cr, uid, ids, vals, context=context)

        # Synchronize to website
        server = get_server(self, cr, uid)
        if callable(server):
            (new, update) = wizard.export_table.export_write(self, cr, uid, server, 'category', ids, vals, context)
        return result


    def create(self, cr, uid, vals, context=None):
        if not context:
            context={}
        #print "create:", vals
        id = super(radiotv_category, self).create(cr, uid, vals, context=context)

        # Synchronize to website
        server = get_server(self, cr, uid)
        if callable(server):
            (new, update) = wizard.export_table.export_write(self, cr, uid, server, 'category', [id], vals, context)
        return id


    def unlink(self, cr, uid, ids):
        #print "ulink:", ids
        result = super(radiotv_category, self).unlink(cr, uid, ids)

        # Synchronize to website
        server = get_server(self, cr, uid)
        if callable(server):
            delete = wizard.export_table.export_ulink(self, cr, uid, server, 'category', ids)
        return result
radiotv_category()


class radiotv_broadcast(osv.osv):
    _name = 'radiotv.broadcast'
    _columns = {
        'dt_start': fields.datetime('Start', required=True),
        'dt_end': fields.datetime('End'),
        'channel_id': fields.many2one('radiotv.channel', 'Channel', required=True),
        'program_id': fields.many2one('radiotv.program', 'Program', required=True, domain=[('state','=','Publish')]),
        'description': fields.text('Description'),
        'url': fields.text('URL'),
    }
    _defaults = {
        'dt_start': lambda *a: time.strftime('%Y-%m-%d 00:00:00'),
        'dt_end': lambda *a: time.strftime('%Y-%m-%d 00:00:00'),
    }
    _order = 'dt_start desc'


    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        res = []
        for r in self.browse(cr, uid, ids):
            name = str(r.program_id.name or '') + ". " + str(r.dt_start)
            res.append((r.id, name))
        return res


    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=250):
        if not args:
            args=[]
        if not context:
            context={}
        ids = []
        if name:
            p = self.pool.get('radiotv.program')
            p_ids = p.search(cr, uid, [('name',operator,name)]+ args, context=context )
            #print "program ids:", p_ids
            ids = self.search(cr, uid, [('program_id','in',p_ids)]+ args, limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, context=context, limit=limit)
        #print "broadcasts ids:", ids
        return self.name_get(cr, uid, ids, context=context)


    def write(self, cr, uid, ids, vals, context=None):
        if not context:
            context={}
        for id in ids:
            bc = self.browse(cr, uid, id)
            if vals.has_key('dt_start'):
                dt_start = vals['dt_start']
            else:
                dt_start = bc.dt_start
            # Change the dt_end field of the record
            if vals.has_key('previous'):
                del vals['previous'] # dt_end of the previous record has been computed
            else:
                cr.execute("SELECT min(dt_start) FROM radiotv_broadcast WHERE channel_id='"+ str(bc.channel_id.id) +"' AND dt_start > '"+ dt_start +"' AND id!='"+ str(id) +"'")
                res = cr.fetchall()[0]
                if res[0]:
                    vals['dt_end'] = res[0]
                else:
                    vals['dt_end'] = dt_start
            
            # Change the dt_end field of the previous record
            if 'dt_start' in vals:
                cr.execute("SELECT max(dt_start) FROM radiotv_broadcast WHERE channel_id='"+ str(bc.channel_id.id) +"' AND dt_start < '"+ dt_start +"' AND id!='"+ str(id) +"'")
                res = cr.fetchall()[0]
                if res[0]:
                    id_prev = self.search(cr, uid, [('channel_id','=',bc.channel_id.id),('dt_start','=',res[0]),] )
                    bc_prev = self.browse(cr, uid, id_prev)
                    vals2 = {}
                    vals2['dt_end'] = vals['dt_start']
                    vals2['previous'] = 1
                    self.write(cr, uid, id_prev, vals2, context)

        #print "write:", ids, vals
        result = super(radiotv_broadcast, self).write(cr, uid, ids, vals, context=context)

        # Synchronize to website
        server = get_server(self, cr, uid)
        if callable(server):
            (new, update) = wizard.export_table.export_write(self, cr, uid, server, 'broadcast', ids, vals, context)
        return result


    def create(self, cr, uid, vals, context=None):
        if not context:
            context={}
        # Change the dt_end field of the record
        if vals.has_key('previous'):
            del vals['previous'] # dt_end of the previous record has been computed
        else:
            cr.execute("SELECT min(dt_start) FROM radiotv_broadcast WHERE channel_id='"+ str(vals['channel_id']) +"' AND dt_start > '"+ vals['dt_start'] +"'")
            res = cr.fetchall()[0]
            if res[0]:
                vals['dt_end'] = res[0]
            else:
                vals['dt_end'] = vals['dt_start']

        # Change the dt_end field of the previous record
        cr.execute("SELECT max(dt_start) FROM radiotv_broadcast WHERE channel_id='"+ str(vals['channel_id']) +"' AND dt_start < '"+ vals['dt_start'] +"'")
        res = cr.fetchall()[0]
        if res[0]:
            id_prev = self.search(cr, uid, [('channel_id','=',vals['channel_id']),('dt_start','=',res[0]),] )
            bc_prev = self.browse(cr, uid, id_prev)
            vals2 = {}
            vals2['dt_end'] = vals['dt_start']
            vals2['previous'] = 1
            self.write(cr, uid, id_prev, vals2, context)

        #print "create:", vals
        id = super(radiotv_broadcast, self).create(cr, uid, vals, context=context)

        # Synchronize to website
        server = get_server(self, cr, uid)
        if callable(server):
            (new, update) = wizard.export_table.export_write(self, cr, uid, server, 'broadcast', [id], vals, context)
        return id


    def unlink(self, cr, uid, ids):
        for id in ids:
            bc = self.browse(cr, uid, id)
            # Change the dt_end field of the previous record
            cr.execute("SELECT max(dt_start) FROM radiotv_broadcast WHERE channel_id='"+ str(bc.channel_id.id) +"' AND dt_start < '"+ bc.dt_start +"' AND id!='"+ str(id) +"'")
            res = cr.fetchall()[0]
            if res[0]:
                id_prev = self.search(cr, uid, [('channel_id','=',bc.channel_id.id),('dt_start','=',res[0]),] )
                bc_prev = self.browse(cr, uid, id_prev)
                vals2 = {}
                vals2['dt_end'] = bc.dt_end
                vals2['previous'] = 1
                self.write(cr, uid, id_prev, vals2)

        #print "ulink:", ids
        result = super(radiotv_broadcast, self).unlink(cr, uid, ids)

        # Synchronize to website
        server = get_server(self, cr, uid)
        if callable(server):
            delete = wizard.export_table.export_ulink(self, cr, uid, server, 'broadcast', ids)
        return result


    def _copy_broadcasts(self, cr, uid, data=False, context={}):
        '''
        Function called by the scheduler to copy broadcasts from the last day wich contain broadcasts to [data] days after
        '''
        import datetime
        #print data
        b = self.pool.get('radiotv.broadcast')
        cr.execute('SELECT max(dt_start) FROM radiotv_broadcast')
        res = cr.fetchall()[0][0]
        day = res[:10]    
        day_max = datetime.date(int(day[:4]), int(day[5:7]), int(day[8:]))
        today_wd = datetime.date.today().weekday()
        offset = today_wd - day_max.weekday()
        if offset > 0:
            offset = offset - 7

        day_interval = datetime.timedelta(days=offset)
        day_from = day_max + day_interval    # day_from is the last day with contain broadcasts with the same weekday as today
        day_interval = datetime.timedelta(days=data)
        day_to = day_from + day_interval    # day_to is [data] days after than day_from (tipically 7)
        d_from = "%04i-%02i-%02i" % (day_from.year, day_from.month, day_from.day)
        d_to   = "%04i-%02i-%02i" % (day_to.year, day_to.month, day_to.day)
        #print d_from, d_to
        
        # deletes previous broadcasts
        broadcast_ids = b.search(cr, uid, [('dt_start','>=','%s 00:00:00' % d_to),('dt_start','<=','%s 23:59:59' % d_to)])
        b.unlink(cr, uid, broadcast_ids)
        
        # copies new broadcasts
        broadcast_ids = b.search(cr, uid, [('dt_start','>=','%s 00:00:00' % d_from),('dt_start','<=','%s 23:59:59' % d_from)])
        for broadcast in b.browse(cr, uid, broadcast_ids, context):
            vals = {
                'dt_start': '%s %s' % (d_to, broadcast.dt_start[11:]),
                'channel_id': broadcast.channel_id.id,
                'program_id': broadcast.program_id.id,
                'description': broadcast.description,
            }
            if broadcast.dt_end:
                vals['dt_end'] = '%s %s' % (d_to, broadcast.dt_end[11:]),
            b.create(cr, uid, vals)
        return {}
radiotv_broadcast()


class radiotv_podcast(osv.osv):
    _name = 'radiotv.podcast'
    _columns = {
        'name': fields.char('Name', size=200, required=True),
        'file_name': fields.char('File name', size=255, required=True),
        'description': fields.text('Description'),
        'broadcast_id': fields.many2one('radiotv.broadcast', 'Broadcast', required=True),
        'author': fields.char('Author', size=255),
        'category': fields.char('Category', size=255),
        'duration': fields.char('Duration', size=10),
        'keywords': fields.char('Keywords', size=255),
        'subtitle': fields.char('Subtitle', size=255),
        'block': fields.boolean('Block'),
        'explicit': fields.boolean('Explicit'),
        'pub_date': fields.datetime('Publication', required=True, readonly=True),
    }
    _defaults = {
        'pub_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'block': lambda *a: False,
        'explicit': lambda *a: False,
    }
    _order = 'name'

    def onchange_broadcast_id(self, cr, uid, ids, broadcast_id):
        v =  {}
        if broadcast_id:
            b = self.pool.get('radiotv.broadcast').browse(cr, uid, broadcast_id)
            v['name'] = b.program_id.name
            if b.description or b.program_id.description:
                v['description'] = b.description or b.program_id.description
            if b.program_id.editor:
                v['author'] = b.program_id.editor
            if b.program_id.category_id:
                v['category'] = b.program_id.category_id.name
            if b.program_id.approx_duration:
                v['duration'] = str(b.program_id.approx_duration)
        return {'value': v}


    def write(self, cr, uid, ids, vals, context=None):
        if not context:
            context={}
        #print "write:", ids, vals
        result = super(radiotv_podcast, self).write(cr, uid, ids, vals, context=context)

        # Synchronize to website
        server = get_server(self, cr, uid)
        if callable(server):
            (new, update) = wizard.export_table.export_write(self, cr, uid, server, 'podcast', ids, vals, context)
        return result


    def create(self, cr, uid, vals, context=None):
        if not context:
            context={}
        #print "create:", vals
        id = super(radiotv_podcast, self).create(cr, uid, vals, context=context)

        # Synchronize to website
        server = get_server(self, cr, uid)
        if callable(server):
            (new, update) = wizard.export_table.export_write(self, cr, uid, server, 'podcast', [id], vals, context)
        return id


    def unlink(self, cr, uid, ids):
        #print "ulink:", ids
        result = super(radiotv_podcast, self).unlink(cr, uid, ids)

        # Synchronize to website
        server = get_server(self, cr, uid)
        if callable(server):
            delete = wizard.export_table.export_ulink(self, cr, uid, server, 'podcast', ids)
        return result
radiotv_podcast()


class radiotv_web(osv.osv):
    _name = "radiotv.web"
    _description = "RadioTV website configuration"
    _columns = {
        'name': fields.char('Name',size=64, required=True),
        'url': fields.char('URL', size=64, required=True),
        'active': fields.boolean('Active'),
        'sync': fields.boolean('Synchronize', help="The changes in channels, programs and broadcasts are synchronized automatically to the website"),
    }
    _defaults = {
        'active': lambda *a: 1
    }
radiotv_web()

