import time
import xmlrpclib
import pooler

import wizard

from urllib import unquote_plus
from re import search as research


_import_done_fields = {
    'num': {'string': 'New Sales Orders', 'readonly': True, 'type': 'integer'}
}

_import_done_form = '''<?xml version="1.0"?>
<form string="Saleorders import">
    <separator string="eSale Orders imported" colspan="4" />
    <field name="num"/>
</form>'''

##         def _decode(name, idn):
##             """DB is corrupted with utf8 and latin1 chars."""
##             decoded_name = name
##             if isinstance(name, unicode):
##                 try:
##                     decoded_name = name.encode('utf8')
##                 except:
##                     decoded_name = name
##             else:
##                 try:
##                     decoded_name = unicode(name, 'utf8')
##                 except:
##                     try:
##                         decoded_name = unicode(name, 'latin1').encode('utf8')
##                     except:
##                         decoded_name = name
## 
##             return decoded_name

def _do_import(self, cr, uid, data, context):
    def _decode(name):
        """DB is corrupted with utf8 and latin1 chars (sometimes urlencoded)."""
        orig_val = unquote_plus(name)

        try:
            decoded_val = u"%s" % (orig_val.encode('latin1').decode('utf8'))
        except UnicodeDecodeError, e:
            decoded_val = orig_val

        return decoded_val

    self.pool = pooler.get_pool(cr.dbname)
    ids = self.pool.get('esale_joomla.web').search(cr, uid, [])
    total = 0
    for website in self.pool.get('esale_joomla.web').browse(cr, uid, ids):
        server = xmlrpclib.ServerProxy("%s/tinyerp-synchro.php" % website.url)

        cr.execute("select max(web_ref) from esale_joomla_order where web_id=%d", (website.id,))
        max_web_id = cr.fetchone()[0]

        saleorders = server.get_saleorders(max_web_id or 0)

        for so in saleorders:
            total += 1
            pids = self.pool.get('esale_joomla.partner').search(cr, uid, [('esale_id', '=', so['delivery']['esale_id'])])

            for addr_obj in ('delivery', 'billing'):
                for key in so[addr_obj].keys():
                    val = _decode(so[addr_obj][key])
                    so[addr_obj][key] = val

            if pids:
                adr_ship = pids[0]
                self.pool.get('esale_joomla.partner').write(cr, uid, pids, so['delivery'])
            else:
                adr_ship = self.pool.get('esale_joomla.partner').create(cr, uid, so['delivery'])

            pids = self.pool.get('esale_joomla.partner').search(cr, uid, [('esale_id', '=', so['billing']['esale_id'])])
            if pids:
                adr_bill = pids[0]
                self.pool.get('esale_joomla.partner').write(cr, uid, pids, so['billing'])
            else:
                adr_bill = self.pool.get('esale_joomla.partner').create(cr, uid, so['billing'])

            order_id = self.pool.get('esale_joomla.order').create(cr, uid, {
                'web_id': website.id,
                'web_ref': so['id'],
                'name': so['id'],
                'date_order': so['date'] or time.strftime('%Y-%m-%d'),
                'note': so['note'] or '',
                'epartner_shipping_id': adr_ship,
                'epartner_invoice_id': adr_bill,
            })

            for orderline in so['lines']:
                ids = None
                if 'product_id' in orderline:
                    ids = self.pool.get('esale_joomla.product').search(cr, uid, [('esale_joomla_id', '=', orderline['product_id']), ('web_id', '=', website.id)])

                if ids:
                    osc_product_id = ids[0]
                    osc_product = self.pool.get('esale_joomla.product').browse(cr, uid, osc_product_id)
                    price = orderline['price']
                    price = float(price) - osc_product.product_id.contrib
                    taxes_included = []
                    for taxe in osc_product.product_id.taxes_id:
                        for t in website.taxes_included_ids:
                            if t.id == taxe.id:
                                taxes_included.append(taxe)
                    for c in self.pool.get('account.tax').compute_inv(cr, uid, taxes_included, price, 1, product=osc_product.product_id):
                        price -= c['amount']

                    self.pool.get('esale_joomla.order.line').create(cr, uid, {
                        'product_id': osc_product.product_id.id,
                        'product_qty': orderline['product_qty'],
                        'name': osc_product.name,
                        'order_id': order_id,
                        'product_uom_id': osc_product.product_id.uom_id.id,
                        'price_unit': price,
                    })

                if 'product_name' in orderline:
                    # special products (like 'Shipping fees'):

                    if "product_is_shipping" in orderline:
                        shipping_product_ids = self.pool.get('product.product').search(cr, uid, [('default_code', '=', '6324')])

                        if shipping_product_ids:
                            shipping_product = self.pool.get('product.product').browse(cr, uid, shipping_product_ids[0])
                            self.pool.get('esale_joomla.order.line').create(cr, uid, {
                                'product_id': shipping_product.id,
                                'product_qty': 1,
                                'name': shipping_product.name,
                                'order_id': order_id,
                                'product_uom_id': shipping_product.uom_id.id,
                                'price_unit': orderline['price']
                            })

        cr.commit()
    return {'num': total}


class wiz_esale_joomla_import_sos(wizard.interface):
    states = {
        'init': {
            'actions': [_do_import],
            'result': {
                'type': 'form',
                'arch': _import_done_form,
                'fields': _import_done_fields,
                'state': [('end', 'End')]
            }
        }
    }

wiz_esale_joomla_import_sos('esale_joomla.saleorders')

