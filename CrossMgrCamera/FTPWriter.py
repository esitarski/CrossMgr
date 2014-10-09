import os
import wx
import ftplib
import datetime
from Queue import Empty

now = datetime.datetime.now()

def FTPWriter( qFTP, qMessage ):
	timeout = 30
	
	keepGoing = True
	while keepGoing:
		message = qFTP.get()
		ftpConnection = None
		loginLast, photoPathLast = None, None
		messages = [message]
		while keepGoing:
			if message[0] == 'save':
				cmd, fname, ftpInfo = message
				
				host = ftpInfo['host']
				user = ftpInfo['user']
				password = ftpInfo['password']
				photoPath = ftpInfo['photoPath']
				
				login = (host, user, password)
				
				try:
					#-------------------------------
					# Login
					#
					if login != loginLast:
						if ftpConnection:
							ftpConnetion.quit()
						ftpConnection = ftplib.FTP( host, timeout=timeout )
						ftpConnection.login( user, password )
						photoPathLast = None
						
					#-------------------------------
					# change to the server path
					#
					if photoPath != photoPathLast:
						if photoPath != '.':
							ftpConnection.cwd( photoPath )
					
					#-------------------------------
					# write file to ftp site
					#
					with open(fname, 'rb') as file:
						ftpConnection.storbinary( 'STOR {}'.format( os.path.basename(fname) ), file )
					
					#-------------------------------
					# store state for next message
					loginLast, photoPathLast = login, photoPath
					
				except Exception as e:
					qMessage.put( ('ftp failure', '"{}": {}'.format(os.path.basename(fname), e) ) )
					loginLast = None
			
			elif message[0] == 'terminate':
				keepGoing = False
			
			qFTP.task_done()
			
			try:
				message = qFTP.get( False )
			except Empty:
				break
		
		if ftpConnection:
			ftpConnetion.quit()
