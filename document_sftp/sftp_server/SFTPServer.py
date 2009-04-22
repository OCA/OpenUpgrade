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
"""
Server-mode SFTP support.
"""

import os
import errno
import paramiko

from Crypto.Hash import MD5, SHA
from paramiko.common import *
from paramiko.server import SubsystemHandler
from paramiko.sftp import *
from paramiko.sftp_si import *
from paramiko.sftp_attr import *

class SFTPServer (paramiko.SFTPServer):

    def _read_folder(self, request_number, folder):        
        flist = folder._get_next_files()        
        if len(flist) == 0:
            self._send_status(request_number, SFTP_EOF)
            return
        msg = Message()
        msg.add_int(request_number)
        msg.add_int(len(flist))
        for node in flist:
            attr = self.server.stat(node)            
            msg.add_string(attr.filename)
            msg.add_string(str(attr))
            attr._pack(msg)
        self._send_packet(CMD_NAME, str(msg))

    def _process(self, t, request_number, msg):                        
        self._log(DEBUG, 'Request: %s' % CMD_NAMES[t])
        datacr = None
        try:
            if t == CMD_OPEN:
                path = msg.get_string()                                
                flags = self._convert_pflags(msg.get_int())                
                if flags & os.O_WRONLY:
                    if flags & os.O_APPEND:
                        fstr = 'ab'
                    else:
                        fstr = 'wb'
                elif flags & os.O_RDWR:
                    if flags & os.O_APPEND:
                        fstr = 'a+b'
                    else:
                        fstr = 'r+b'
                else:
                    # O_RDONLY (== 0)
                    fstr = 'rb'                
                if fstr in ('wb'):
                    basedir,basename = os.path.split(path)                    
                    datacr = self.server.get_cr(path)                    
                    node = self.server.ftp2fs(basedir, datacr)
                    self._send_handle_response(request_number, self.server.create(node, basename,flags))
                else:                    
                    attr = False #SFTPAttributes._from_msg(msg)                    
                    datacr = self.server.get_cr(path)                    
                    node = self.server.ftp2fs(path, datacr)                                             
                    self._send_handle_response(request_number, self.server.open(node, flags, attr))
            elif t == CMD_CLOSE:
                handle = msg.get_string()
                if handle in self.folder_table:                    
                    del self.folder_table[handle]
                    self._send_status(request_number, SFTP_OK)
                    return
                if handle in self.file_table:                    
                    self.file_table[handle].close()                    
                    del self.file_table[handle]                    
                    self._send_status(request_number, SFTP_OK)
                    return
                self._send_status(request_number, SFTP_BAD_MESSAGE, 'Invalid handle')
            elif t == CMD_READ:               
                handle = msg.get_string()
                offset = msg.get_int64()
                length = msg.get_int()                
                if handle not in self.file_table:
                    self._send_status(request_number, SFTP_BAD_MESSAGE, 'Invalid handle')
                    return
                data = self.file_table[handle].read(offset, length)
                if type(data) is str:
                    if len(data) == 0:
                        self._send_status(request_number, SFTP_EOF)
                    else:
                        self._response(request_number, CMD_DATA, data)
                else:
                    self._send_status(request_number, data)
            elif t == CMD_WRITE:                
                handle = msg.get_string()                
                offset = msg.get_int64()
                data = msg.get_string()                
                if handle not in self.file_table:
                    self._send_status(request_number, SFTP_BAD_MESSAGE, 'Invalid handle')
                    return
                self._send_status(request_number, self.file_table[handle].write(offset, data))
            elif t == CMD_REMOVE:
                path = msg.get_string()                
                datacr = self.server.get_cr(path)                
                node = self.server.ftp2fs(path, datacr)                
                self._send_status(request_number, self.server.remove(node))
            elif t == CMD_RENAME:
                oldpath = msg.get_string()
                newpath = msg.get_string()
                datacr = self.server.get_cr(oldpath)
                src = self.server.ftp2fs(oldpath, datacr)
                #line = self.fs.ftpnorm(line)
                basedir,basename = os.path.split(newpath)
                dst = self.server.ftp2fs(basedir, datacr)                
                self._send_status(request_number, self.server.rename(src, dst,basename))
            elif t == CMD_MKDIR:
                path = msg.get_string()
                attr = SFTPAttributes._from_msg(msg)
                basedir,basename = os.path.split(path)
                datacr = self.server.get_cr(path)
                node = self.server.ftp2fs(basedir, datacr)
                self._send_status(request_number, self.server.mkdir(node,basename, attr))
            elif t == CMD_RMDIR:
                path = msg.get_string()
                datacr = self.server.get_cr(path)
                node = self.server.ftp2fs(path, datacr)
                #line = self.server.ftpnorm(line)
                self._send_status(request_number, self.server.rmdir(node))
            elif t == CMD_OPENDIR:
                path = msg.get_string()                
                datacr = self.server.get_cr(path)
                node = self.server.ftp2fs(path, datacr)                
                self._open_folder(request_number, node)
                return
            elif t == CMD_READDIR:
                handle = msg.get_string()
                if handle not in self.folder_table:
                    self._send_status(request_number, SFTP_BAD_MESSAGE, 'Invalid handle')
                    return
                folder = self.folder_table[handle]
                self._read_folder(request_number, folder)
            elif t == CMD_STAT:
                path = msg.get_string()                                
                datacr = self.server.get_cr(path)                
                node = self.server.ftp2fs(path, datacr)                                
                resp = self.server.stat(node)                
                if issubclass(type(resp), SFTPAttributes):
                    self._response(request_number, CMD_ATTRS, resp)
                else:
                    self._send_status(request_number, resp)
            elif t == CMD_LSTAT:
                path = msg.get_string()                    
                datacr = self.server.get_cr(path)                
                node = self.server.ftp2fs(path, datacr)                  
                resp = self.server.lstat(node)
                if issubclass(type(resp), SFTPAttributes):
                    self._response(request_number, CMD_ATTRS, resp)
                else:
                    self._send_status(request_number, resp)
            elif t == CMD_FSTAT:
                handle = msg.get_string()
                if handle not in self.file_table:
                    self._send_status(request_number, SFTP_BAD_MESSAGE, 'Invalid handle')
                    return
                resp = self.file_table[handle].stat()
                if issubclass(type(resp), SFTPAttributes):
                    self._response(request_number, CMD_ATTRS, resp)
                else:
                    self._send_status(request_number, resp)
            elif t == CMD_SETSTAT:
                path = msg.get_string()
                attr = SFTPAttributes._from_msg(msg)
                self._send_status(request_number, self.server.chattr(path, attr))
            elif t == CMD_FSETSTAT:
                handle = msg.get_string()
                attr = SFTPAttributes._from_msg(msg)
                if handle not in self.file_table:
                    self._response(request_number, SFTP_BAD_MESSAGE, 'Invalid handle')
                    return
                self._send_status(request_number, self.file_table[handle].chattr(attr))
            elif t == CMD_READLINK:
                path = msg.get_string()
                resp = self.server.readlink(path)
                if type(resp) is str:
                    self._response(request_number, CMD_NAME, 1, resp, '', SFTPAttributes())
                else:
                    self._send_status(request_number, resp)
            elif t == CMD_SYMLINK:
                # the sftp 2 draft is incorrect here!  path always follows target_path
                target_path = msg.get_string()
                path = msg.get_string()
                self._send_status(request_number, self.server.symlink(target_path, path))
            elif t == CMD_REALPATH:
                path = msg.get_string()
                rpath = self.server.canonicalize(path)
                self._response(request_number, CMD_NAME, 1, rpath, '', SFTPAttributes())
            elif t == CMD_EXTENDED:
                tag = msg.get_string()
                if tag == 'check-file':
                    self._check_file(request_number, msg)
                else:
                    self._send_status(request_number, SFTP_OP_UNSUPPORTED)
            else:
                self._send_status(request_number, SFTP_OP_UNSUPPORTED)
        finally:
            if datacr :
                self.server.close_cr(datacr)
