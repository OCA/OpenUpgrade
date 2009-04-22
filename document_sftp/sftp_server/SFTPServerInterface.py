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
import os
import paramiko,os
import pooler
import netsvc
import time
import StringIO
import base64

from paramiko.sftp_handle import SFTPHandle

class file_wrapper(StringIO.StringIO):
    def __init__(self, sstr='', ressource_id=False, dbname=None, uid=1, name=''):
        StringIO.StringIO.__init__(self, sstr)         
        self.ressource_id = ressource_id
        self.name = name
        self.dbname = dbname
        self.uid = uid
    def close(self, *args, **kwargs):        
        db,pool = pooler.get_db_and_pool(self.dbname)        
        self.buf = ''
        cr = db.cursor()
        cr.commit()        
        try:
            val = self.getvalue()            
            val2 = {
                'datas': base64.encodestring(val),
                'file_size': len(val),
            }            
            pool.get('ir.attachment').write(cr, self.uid, [self.ressource_id], val2)           
        
        finally:
            cr.commit()
            cr.close()
        return StringIO.StringIO.close(self, *args, **kwargs)

class content_wrapper(StringIO.StringIO):
    def __init__(self, dbname, uid, pool, node, name=''):
        StringIO.StringIO.__init__(self, '')                
        self.dbname = dbname
        self.uid = uid
        self.node = node
        self.pool = pool
        self.name = name
    def close(self, *args, **kwargs):
        db,pool = pooler.get_db_and_pool(self.dbname)
        cr = db.cursor()
        cr.commit()        
        try:
            getattr(self.pool.get('document.directory.content'), 'process_write_'+self.node.content.extension[1:])(cr, self.uid, self.node, self.getvalue())
        finally:
            cr.commit()
            cr.close()
        return StringIO.StringIO.close(self, *args, **kwargs)

class SFTPServer (paramiko.SFTPServerInterface):
    db_name_list=[]
    def __init__(self, server, *largs, **kwargs):        
        self.server = server        
        self.ROOT = '/'

    def fs2ftp(self, node):        
        res='/'
        if node:
            res=os.path.normpath(node.path)
            res = res.replace("\\", "/")        
            while res[:2] == '//':
                res = res[1:]
            res='/' + node.cr.dbname + '/' + res
        return res

    def ftp2fs(self, path, data):        
        if not data or (path and (path in ('/','.'))):
            return None               
        path2 = filter(None,path.split('/'))[1:]                
        (cr, uid, pool) = data        
        res = pool.get('document.directory').get_object(cr, uid, path2[:])                
        if not res:
            raise OSError(2, 'Not such file or directory.')
        return res

    def get_cr(self, path):              
        if path and path in ('/','.'):
            return None
        dbname = path.split('/')[1]         
        try:
            if not len(self.db_name_list):
                self.db_name_list = self.db_list()
            if dbname not in self.db_name_list:
                return None            
            db,pool = pooler.get_db_and_pool(dbname)            
        except:
            raise OSError(1, 'Operation not permited.')
        cr = db.cursor()        
        uid = self.server.check_security(dbname, self.server.username, self.server.key)        
        if not uid:
            raise OSError(2, 'Authentification Required.')
        return cr, uid, pool

    def close_cr(self, data):
        if data:
            data[0].close()
        return True


    def open(self, node, flags, attr):        
        try:
            if not node:
                raise OSError(1, 'Operation not permited.')                        
            if node.type=='file':                
                if not self.isfile(node):
                    raise OSError(1, 'Operation not permited.')
                f = StringIO.StringIO(base64.decodestring(node.object.datas or ''))                
            elif node.type=='content':
                cr = node.cr
                uid = node.uid
                pool = pooler.get_pool(cr.dbname)
                f=getattr(pool.get('document.directory.content'), 'process_read_'+node.content.extension[1:])(cr, uid, node)
            else:
                raise OSError(1, 'Operation not permited.')
        except OSError, e:
            return paramiko.SFTPServer.convert_errno(e.errno)

        fobj = SFTPHandle(flags)
        fobj.filename = node.path
        fobj.readfile = f
        fobj.writefile = None       
        return fobj       

    def create(self, node, objname, flags):        
        cr = node.cr
        uid = node.uid
        pool = pooler.get_pool(cr.dbname)
        child = node.child(objname)
        f = None
        if child:
            if child.type in ('collection','database'):
                raise OSError(1, 'Operation not permited.')
            if child.type=='content':
                f = content_wrapper(cr.dbname, uid, pool, child)
                
        try:
            fobj = pool.get('ir.attachment')
            ext = objname.find('.') >0 and objname.split('.')[1] or False

            # TODO: test if already exist and modify in this case if node.type=file
            ### checked already exits
            object2=node and node.object2 or False
            object=node and node.object or False
            cid=False

            where=[('name','=',objname)]
            if object and (object.type in ('directory')) or object2:
                where.append(('parent_id','=',object.id))
            else:
                where.append(('parent_id','=',False))

            if object2:
                where +=[('res_id','=',object2.id),('res_model','=',object2._name)]
            cids = fobj.search(cr, uid,where)
            if len(cids):
                cid=cids[0]

            if not cid:
                val = {
                    'name': objname,
                    'datas_fname': objname,
                    'datas': '',
                    'file_size': 0L,
                    'file_type': ext,
                }
                if object and (object.type in ('directory')) or not object2:
                    val['parent_id']= object and object.id or False
                partner = False
                if object2:
                    if 'partner_id' in object2 and object2.partner_id.id:
                        partner = object2.partner_id.id
                    if object2._name == 'res.partner':
                        partner = object2.id
                    val.update( {
                        'res_model': object2._name,
                        'partner_id': partner,
                        'res_id': object2.id
                    })
                cid = fobj.create(cr, uid, val, context={})
            cr.commit()

            f = file_wrapper('', cid, cr.dbname, uid, )          
            
        except Exception,e:             
            log(e)
            raise OSError(1, 'Operation not permited.')

        if f :
            fobj = SFTPHandle(flags)
            fobj.filename =  objname
            fobj.readfile = None
            fobj.writefile = f
            return fobj
        return False

    def remove(self, node):   
        """ Remove a file """
        try:       
            print ' ......... Remove ......', node     
            cr = node.cr
            uid = node.uid
            pool = pooler.get_pool(cr.dbname)
            object2=node and node.object2 or False
            object=node and node.object or False
            if not object:
                raise OSError(2, 'Not such file or directory.')
            if object._table_name=='ir.attachment':
                res = pool.get('ir.attachment').unlink(cr, uid, [object.id])
            else:
                raise OSError(1, 'Operation not permited.')
            cr.commit()
            return paramiko.SFTP_OK
        except OSError, e:
            return paramiko.SFTPServer.convert_errno(e.errno)

    def db_list(self):
        #return pooler.pool_dic.keys()                
        s = netsvc.LocalService('db')
        result = s.list()
        self.db_name_list = []
        for db_name in result:
            db, cr = None, None
            try:
                db = pooler.get_db_only(db_name)
                cr = db.cursor()
                cr.execute("SELECT 1 FROM pg_class WHERE relkind = 'r' AND relname = 'ir_module_module'")
                if not cr.fetchone():
                    continue

                cr.execute("select id from ir_module_module where name like 'document%' and state='installed' ")
                res = cr.fetchone()
                if res and len(res):
                    self.db_name_list.append(db_name)
                cr.commit()
            except Exception,e:
                log(e)
                if cr:
                    cr.rollback()
            finally:
                if cr is not None:
                    cr.close()                   
        return self.db_name_list

    def list_folder(self, node):
        """ List the contents of a folder """        
        try:
            """List the content of a directory."""
            class false_node:
                object = None
                type = 'database'
                def __init__(self, db):
                    self.path = '/'+db

            if node is None:
                result = []
                for db in self.db_list():                    
                    uid = self.server.check_security(db, self.server.username, self.server.key)        
                    if uid:
                        result.append(false_node(db))                
                return result
            return node.children()
        except OSError, e:
            return paramiko.SFTPServer.convert_errno(e.errno)

    def rename(self, src, dst_basedir,dst_basename):
        """
            Renaming operation, the effect depends on the src:
            * A file: read, create and remove
            * A directory: change the parent and reassign childs to ressource
        """
        try:
            #dst_basename=_to_unicode(dst_basename)
            if src.type=='collection':
                if src.object._table_name <> 'document.directory':
                    raise OSError(1, 'Operation not permited.')
                result = {
                    'directory': [],
                    'attachment': []
                }
                # Compute all childs to set the new ressource ID
                child_ids = [src]
                while len(child_ids):
                    node = child_ids.pop(0)
                    child_ids += node.children()
                    if node.type =='collection':
                        result['directory'].append(node.object.id)
                        if (not node.object.ressource_id) and node.object2:
                            raise OSError(1, 'Operation not permited.')
                    elif node.type =='file':
                        result['attachment'].append(node.object.id)

                cr = src.cr
                uid = src.uid
                pool = pooler.get_pool(cr.dbname)
                object2=src and src.object2 or False
                object=src and src.object or False
                if object2 and not object.ressource_id:
                    raise OSError(1, 'Operation not permited.')
                val = {
                    'name':dst_basename,
                }
                if (dst_basedir.object and (dst_basedir.object.type in ('directory'))) or not dst_basedir.object2:
                    val['parent_id'] = dst_basedir.object and dst_basedir.object.id or False
                else:
                    val['parent_id'] = False
                res = pool.get('document.directory').write(cr, uid, [object.id],val)

                if dst_basedir.object2:
                    ressource_type_id = pool.get('ir.model').search(cr,uid,[('model','=',dst_basedir.object2._name)])[0]
                    ressource_id = dst_basedir.object2.id
                    title = dst_basedir.object2.name
                    ressource_model = dst_basedir.object2._name                    
                    if dst_basedir.object2._name=='res.partner':
                        partner_id=dst_basedir.object2.id
                    else:
                        obj2=pool.get(dst_basedir.object2._name)                         
                        partner_id= obj2.fields_get(cr,uid,['partner_id']) and dst_basedir.object2.partner_id.id or False
                else:
                    ressource_type_id = False
                    ressource_id=False
                    ressource_model = False
                    partner_id = False
                    title = False

                pool.get('document.directory').write(cr, uid, result['directory'], {
                    'ressource_id': ressource_id,
                    'ressource_type_id': ressource_type_id
                })
                val = {
                    'res_id': ressource_id,
                    'res_model': ressource_model,
                    'title': title,
                    'partner_id': partner_id
                }
                pool.get('ir.attachment').write(cr, uid, result['attachment'], val)
                if (not val['res_id']) and result['attachment']:
                    dst_basedir.cr.execute('update ir_attachment set res_id=NULL where id in ('+','.join(map(str,result['attachment']))+')')

                cr.commit()
            elif src.type=='file':
                pool = pooler.get_pool(src.cr.dbname)
                val = {
                    'partner_id':False,
                    #'res_id': False,
                    'res_model': False,
                    'name': dst_basename,
                    'datas_fname': dst_basename,
                    'title': dst_basename,
                }

                if (dst_basedir.object and (dst_basedir.object.type in ('directory','ressource'))) or not dst_basedir.object2:
                    val['parent_id'] = dst_basedir.object and dst_basedir.object.id or False
                else:
                    val['parent_id'] = False

                if dst_basedir.object2:
                    val['res_model'] = dst_basedir.object2._name
                    val['res_id'] = dst_basedir.object2.id
                    val['title'] = dst_basedir.object2.name
                    if dst_basedir.object2._name=='res.partner':
                        val['partner_id']=dst_basedir.object2.id
                    else:
                        obj2=pool.get(dst_basedir.object2._name) 
                        val['partner_id']= obj2.fields_get(cr,uid,['partner_id']) and dst_basedir.object2.partner_id.id or False
                elif src.object.res_id:
                    # I had to do that because writing False to an integer writes 0 instead of NULL
                    # change if one day we decide to improve osv/fields.py
                    dst_basedir.cr.execute('update ir_attachment set res_id=NULL where id=%s', (src.object.id,))

                pool.get('ir.attachment').write(src.cr, src.uid, [src.object.id], val)
                src.cr.commit()
            elif src.type=='content':
                src_file=self.open(src,'r')
                dst_file=self.create(dst_basedir,dst_basename,'w')
                dst_file.write(src_file.getvalue())
                dst_file.close()
                src_file.close()
                src.cr.commit()
            else:
                raise OSError(1, 'Operation not permited.')
            return paramiko.SFTP_OK
        except Exception,err:
            log(err)
            return paramiko.SFTPServer.convert_errno(e.errno)

   

    
        

    def mkdir(self, node, basename,attr):
        try:
            """Create the specified directory."""            
            if not node:
                raise OSError(1, 'Operation not permited.')
            
            #basename=_to_unicode(basename)
            object2=node and node.object2 or False
            object=node and node.object or False
            cr = node.cr
            uid = node.uid
            pool = pooler.get_pool(cr.dbname)
            if node.object and (node.object.type=='ressource') and not node.object2:
                raise OSError(1, 'Operation not permited.')
            val = {
                'name': basename,
                'ressource_parent_type_id': object and object.ressource_type_id.id or False,
                'ressource_id': object2 and object2.id or False
            }
            if (object and (object.type in ('directory'))) or not object2:                
                val['parent_id'] =  object and object.id or False
            # Check if it alreayd exists !
            pool.get('document.directory').create(cr, uid, val)
            cr.commit()
           
            return paramiko.SFTP_OK
        except Exception,err:
            return paramiko.SFTPServer.convert_errno(e.errno)

    def rmdir(self, node):
        try:           
            cr = node.cr
            uid = node.uid
            pool = pooler.get_pool(cr.dbname)
            object2=node and node.object2 or False
            object=node and node.object or False
            if object._table_name=='document.directory':
                if node.children():
                    raise OSError(39, 'Directory not empty.')
                res = pool.get('document.directory').unlink(cr, uid, [object.id])
            else:
                raise OSError(39, 'Directory not empty.')

            cr.commit()
            return paramiko.SFTP_OK
        except OSError, e:
            return paramiko.SFTPServer.convert_errno(e.errno)

    def _realpath(self, path):
        """ Enforce the chroot jail """        
        path = self.ROOT + self.canonicalize(path)        
        return path  

    def isfile(self, node):
        if node and (node.type not in ('collection','database')):
            return True
        return False

    
    def islink(self, node):
        """Return True if path is a symbolic link."""
        return False

    
    def isdir(self, node):
        """Return True if path is a directory."""
        if not node:
            return False
        if node and (node.type in ('collection','database')):
            return True
        return False

   
    def getsize(self, node):
        """Return the size of the specified file in bytes."""
        result = 0L
        if node and node.type=='file':
            result = node.object.file_size or 0L
        return result

    
    def getmtime(self, node):
        """Return the last modified time as a number of seconds since
        the epoch."""
        if node and node.object and node.type<>'content':
            dt = (node.object.write_date or node.object.create_date)[:19]
            result = time.mktime(time.strptime(dt, '%Y-%m-%d %H:%M:%S'))
        else:
            result = time.mktime(time.localtime())
        return result


    """ Represents a handle to an open file """
    def stat(self,node):        
        try:
            r = list(os.stat('/'))            
            if self.isfile(node):
                r[0] = 33188  
            if self.isdir(node):
                r[0] = 16877                
            r[6] = self.getsize(node)                    
            r[7] = self.getmtime(node)               
            r[8] =  self.getmtime(node)            
            r[9] =  self.getmtime(node)               
            return paramiko.SFTPAttributes.from_stat(os.stat_result(r),node and node.path.split('/')[-1] or '.')
        except OSError, e:            
            return paramiko.SFTPServer.convert_errno(e.errno)
    lstat=stat        


    
    

    def chattr(self, path, attr):
        return paramiko.SFTP_OK

    def symlink(self, target_path, path):
        return paramiko.SFTP_OK

    def readlink(self, path):
        return paramiko.SFTP_NO_SUCH_FILE
