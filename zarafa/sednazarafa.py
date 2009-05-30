#!/usr/bin/env python
#coding: utf-8
#
# (c) 2008 Sednacom <http://www.sednacom.fr>
#
# authors :
#  - Brice V. < brice@sednacom.fr >

from osv import osv, fields
import StringIO
import urllib2

_ZARAFA_TINYERP_MAP = {
    'zid' : 'zarafa_id' ,
    'name' : 'name' ,
    'email' : 'email' ,
    'company' : 'partner_id' ,
    'phone' : 'phone' ,
    'mobile' : 'mobile' ,
    'fax' : 'fax' ,
}

_MARK_START = 'contact start'
_MARK_END = 'contact end'

_ZARAFA_CONTACT_URL = 'http://%(zarafa_server)s/webaccess/' \
        'contact.php?user=%(zarafa_user)s' \
        '&pwd=%(zarafa_password)s'

class res_partner_address(osv.osv):
    """Address, with new data for zarafa"""
    _name = 'res.partner.address'
    _inherit = 'res.partner.address'
    _description = __doc__

    _columns = {
        'zarafa_id' : fields.char('Z-Id', size=128),
    }

    def unlink(self, cr, uid, rpa_ids, context={}):
        zids = ', '.join(["'%s'" % val["zarafa_id"] for val in \
                    self.read(cr, uid, rpa_ids, ["zarafa_id",]) \
                        if val["zarafa_id"] ])
        res = super(res_partner_address, self).unlink(cr, uid, rpa_ids, context)
        sql = "delete from zarafa_contact where zid in (%s)" % zids
        cr.execute(sql)
        return res

res_partner_address()

class zarafa_contact(osv.osv):
    """Contacts, with features to import from Zarafa server"""
    _name = 'zarafa.contact'
    _description = __doc__

    _columns = {
        'name' : fields.char('Name', size=128, required=True) ,
        'email' : fields.char('Email', size=128, required=True) ,
        'phone' : fields.char('Phone', size=128) ,
        'mobile' : fields.char('Mobile', size=128) ,
        'fax' : fields.char('Fax', size=128) ,
        'company' : fields.char('Company', size=128) ,
        'zid' : fields.char('Z-Id', size=128, required=True) ,
        'state' : fields.selection(
            [   ('new','New'),
                ('update','Update'), ] ,
            'State', readonly=True,) ,
    }

    def _import(self, cr, uid, context={}):
        data = self._get_zarafa_contacts(cr, uid, context)
        res = self._proc_data(cr, uid, data, context)
        self._do_rpa(cr, uid, self.search(cr, uid, []))
        return True

    def _get_zarafa_contacts(self, cr, uid, context={}):

        o_ru = self.pool.get('res.users')
        zud = o_ru.read(cr, uid, [uid,], ['zarafa_server', 'zarafa_user', 'zarafa_password'])[0]

        zurl = _ZARAFA_CONTACT_URL % zud
        ures = urllib2.urlopen(zurl)

        return ures.read()

    def _proc_data(self, cr, uid, data, context={}):
        sio = StringIO.StringIO(data)

        res = []
        while True:
            try:
                cur_val = sio.next().strip()
            except StopIteration:
                break
            if cur_val == 'contact start':
                vals = {}
            elif cur_val == 'contact end':
                res.append(vals)
            else:
                if not cur_val:
                    continue
                fn, fv = cur_val.split(':')
                vals[fn.strip()] = fv.strip()
                if fn == 'zid':
                    zids = self.search(cr, uid, [('zid','=',fv),])
                    if zids:
                        vals['state'] = 'update:%s' % zids[0]
                    else:
                        vals['state'] = 'new'

        for val in res:
            if val['state'] == 'new':
                self.create(cr, uid, val)
            else:
                state = val['state']
                val['state'],zid = state.split(':')
                self.write(cr, uid, int(zid), val)

        return res

    def _do_rpa(self, cr, uid, zcids, context={}):
        data = self.read(cr, uid, zcids, ['id', 'state', ])
        to_create = []
        to_update = []
        for row in data:
            if row['state'] == 'new':
                to_create.append(row['id'])
            else:
                to_update.append(row['id'])

        self._create_contact(cr, uid, to_create, context)
        self._update_contact(cr, uid, to_update, context)

        return True

    def _get_partner(self, cr, uid, name, context={}):
        o_rp =  self.pool.get('res.partner')
        rp_ids = o_rp.search(cr, uid, [('name','=',name),])
        if rp_ids:
            rp_id = rp_ids[-1]
        else:
            rp_id = o_rp.create(cr, uid, {'name' : name})
        return rp_id

    def _create_contact(self, cr, uid, zcids, context={}):
        o_rpa = self.pool.get('res.partner.address')
        o_rp =  self.pool.get('res.partner')
        res = list()
        for data in self.browse(cr, uid, zcids, context):
            part_id = self._get_partner(cr, uid, data.company or data.name, context)
            vals = {
                'name' : data.name ,
                'email' : data.email ,
                'phone' : data.phone ,
                'mobile' : data.mobile ,
                'fax' : data.fax ,
                'zarafa_id' : data.zid ,
                'partner_id' : part_id ,
            }
            o_rpa.create(cr, uid, vals, context)
            res.append(data.id)
        self.write(cr, uid, res, {'state' : 'update'})
        return res

    def _update_contact(self, cr, uid, zcids, context={}):
        o_rpa = self.pool.get('res.partner.address')
        res = list()
        for data in self.browse(cr, uid, zcids, context):
            try:
                rpa_id = o_rpa.search(cr, uid, [('zarafa_id','=',data.zid),])[0]
            except IndexError:
                return self._create_contact(cr, uid, [data.id, ], context)
            vals = {
                'name' : data.name ,
                'email' : data.email ,
                'phone' : data.phone ,
                'mobile' : data.mobile ,
                'fax' : data.fax ,
            }
            o_rpa.write(cr, uid, rpa_id, vals)
            res.append(data.id)
        return res


zarafa_contact()


class res_users(osv.osv):
    """Users with Zarafa connection"""
    _name = 'res.users'
    _inherit = 'res.users'

    _columns = {
        'zarafa_server' : fields.char("Zarafa server", size=128) ,
        'zarafa_user' : fields.char("Zarafa user", size=64) ,
        'zarafa_password' : fields.char("Zarafa password", size=64, invisible=True) ,
        'zarafa_email' : fields.char("Zarafa email", size=64) ,
    }

res_users()
