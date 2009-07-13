#!/usr/bin/python

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

import paramiko, socket, threading
from Server import Server
import SFTPServerInterface
import SFTPServer
from document import ftpserver 
from tools import config
import os

privateKey = os.path.expanduser('~/.ssh/id_rsa')
PORT = int(config.get('sftp_server_port', 8022))
HOST = ''

class sftp_server(ftpserver.ftp_server):  
    def log(self, level, message):        
        logger = netsvc.Logger()
        logger.notifyChannel('SFTP', level, message)

    def run(self):        
        #paramiko.util.log_to_file('paramiko.log')
        # get host private key
        host_key = paramiko.RSAKey(filename=privateKey)

        # bind the socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', PORT))

        # listen for a connection
        sock.listen(50)

        # accept connections
        while True:
            client, addr = sock.accept()

            try:
                # set up server
                t = paramiko.Transport(client)
                
                t.load_server_moduli()
                t.add_server_key(host_key)

                # set up sftp handler
                t.set_subsystem_handler('sftp', SFTPServer.SFTPServer, SFTPServerInterface.SFTPServer)
                server = Server()
                event = threading.Event()

                # start ssh server session
                t.start_server(event, server)

            except Exception, e:
                try:
                    t.close()
                except:
                    pass
                raise

ds = sftp_server()
ds.start()











