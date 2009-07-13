from urllib import urlencode
import urllib2
import mimetypes
import base64

try:
    from hashlib import md5
except ImportError:
    from md5 import md5

from osv import osv, fields


def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be 
    uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = '\r\n'
    L = []
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"'
                     % (key, filename))
        L.append('Content-Type: %s' % get_content_type(filename))
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'    

def vt(res):
    scheme = ['http', 'https'][hasattr(urllib2, 'HTTPSHandler')]
    return '%s://www.virustotal.com/vt/en/%s' % (scheme, res)

class attachment(osv.osv):
    _inherit = 'ir.attachment'

    def _get_vt_status_pict(self, cr, uid, ids, name, args, context):
        res = {}
        for attach in self.browse(cr, uid, ids, context=context):
            # update the status 'scanning' to the real status
            if attach.vt_status == 'scanning' and attach.vt_url:
                ident = attach.vt_url.split('/')[-1]
                url = vt('resultado?%s-0-0' % (ident,))
                uo = urllib2.urlopen(url)
                resultado = eval(uo.read())
                if resultado[0] == 'TERMINADO':
                    clean = all(r[3] == '-' for r in resultado[2])
                    attach.write({'vt_status': ['infected', 'clean'][clean]})
                elif resultado[0] in 'CADUCADO':
                    # file has expired. 
                    ## repost the file? 
                    ## or a new state? so append the report to the attachment
                    pass
                
                cr.commit()

            stock = {
                'nottested': 'STOCK_DIALOG_QUESTION',
                'scanning': 'STOCK_EXECUTE',
                'clean': 'STOCK_APPLY',
                'infected': 'STOCK_STOP',
            }.get(attach.vt_status, '')
            res[attach.id] = ('stock', (stock, 'ICON_SIZE_MENU'))
        return res

    def search_viruses(self, cr, uid, ids, context=None):
        self.check(cr, uid, ids, 'write')
        for attach in self.browse(cr, uid, ids, context={'bin_size': False}):
            if not attach.datas or attach.vt_url:
                continue
            
            data = base64.decodestring(attach.datas)

            digest = md5(data).hexdigest()
            uo = urllib2.urlopen(vt('consultamd5'), 
                                 urlencode({'hash': digest}))
            url = uo.geturl()
            if url.endswith('?notfound'):
                identificador = urllib2.urlopen(vt('identificador')).read()

                content_type, post_data = encode_multipart_formdata(
                    [('distribuir', '1')], 
                    [('archivo', str(attach.datas_fname), data)]
                )
                headers = {
                    'Content-type': content_type,
                    'Accept': '*/*',
                }
                request = urllib2.Request(
                    vt('recepcion?%s' % (identificador,)),
                    post_data,
                    headers
                )
                uo = urllib2.urlopen(request)
                url = uo.geturl()
            
            attach.write({'vt_url': url, 'vt_status': 'scanning'})
        return True
    
    def write(self, cr, uid, ids, values, context=None):
        if 'datas' in values:
            values['vt_url'] = False
            values['vt_status'] = 'nottested'

        return super(attachment, self).write(cr, uid, ids, values, context)

    _columns = {
        'vt_url': fields.char('VirusTotal URL', size=68, readonly=True),
        'vt_status': fields.selection(
            string='VirusTotal status',
            selection=[('nottested', 'Not Tested'), ('scanning', 'Scanning'), 
                       ('clean', 'Clean'), ('infected', 'Infected')],
            readonly=True),
        'vt_status_pict': fields.function(_get_vt_status_pict, method=True, 
                                          type='picture'),
    }

    _defaults = {
        'vt_status': lambda *a: 'nottested',
    }


attachment()

