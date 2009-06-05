Introduction
============
Using this module, DMS can suuport SFTP protocall. 
In this module ,we have Implemented paramiko-1.7.4 lib

You have to register your system ssh key in user form. DMS will be used this public key to verify authetication on file transfer.

Here We have FIX in code :
    SFTP server host : 'localhost'
    SFTP Server port : 8022
    allowed authetication type : 'publickey'

if you want to change allowed authetication type like 'password' or 'none', you have to change value of 'allowed_auths' in 'document_sftp / sftp_server / Server.py'.
if you want to change host/ port for SFTP server, you have to change it from 'document_sftp / sftp_server / __init__.py'.


you have to install paramiko-1.7.4 python module before install this module. you can download paramiko lib from (http://www.lag.net/paramiko/?ref=darwinports.com) 


