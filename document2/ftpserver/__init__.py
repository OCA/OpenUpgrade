import ftpserver
import authorizer
import abstracted_fs

PORT = 8021
HOST = ''


authorizer = authorizer.authorizer()
ftpserver.FTPHandler.authorizer = authorizer
ftpserver.FTPHandler.abstracted_fs = abstracted_fs.abstracted_fs
address = (HOST, PORT)
ftpd = ftpserver.FTPServer(address, ftpserver.FTPHandler)
ftpd.serve_forever()


