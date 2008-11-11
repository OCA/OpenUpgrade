import wizard
import pooler
import xmlrpclib
import netsvc


class server_common:
    def __init__(self, cr, uid):
        self.logger = netsvc.Logger()
        self.pool = pooler.get_pool(cr.dbname)
        
        magento_web_id = self.pool.get('magento.web').search(cr, uid,[('magento_id','=',1)])
        try:
            magento_web = self.pool.get('magento.web').browse(cr, uid, magento_web_id[0])
            self.server = xmlrpclib.ServerProxy("%sindex.php/api/xmlrpc" % magento_web.magento_url)   
        except:
            raise wizard.except_wizard("UserError", "You must have a declared website with a valid URL, a Magento username and password")
        try:
            try:
                self.session = self.server.login(magento_web.api_user, magento_web.api_pwd)
            except xmlrpclib.Fault,error:
                raise wizard.except_wizard("MagentoError", "Magento returned %s" % error)
        except:
            raise wizard.except_wizard("ConnectionError", "Couldn't connect to Magento with URL %sindex.php/api/xmlrpc" % magento_web.magento_url)