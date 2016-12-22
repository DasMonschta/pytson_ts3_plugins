from ts3plugin import ts3plugin, PluginHost

import ts3, ts3defines, os.path, time
from configparser import ConfigParser
from ts3 import getPluginPath

from os import path

from PythonQt.QtSql import QSqlDatabase

from PythonQt.QtGui import *
from PythonQt.QtCore import Qt

from pytsonui import *


#if not self.dlg: self.dlg = QDialog()
#self.dlg.show()
#self.dlg.resize(300,200)	


#(error, name) = ts3.getClientVariableAsInt(schid, clientID, ts3defines.ClientProperties.CLIENT_NICKNAME)

#if name == "Götzenbild_":
#	(error, dbid) = ts3.getClientVariableAsUInt64(schid, clientID, ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
#	ts3.requestSetClientChannelGroup(schid, [12], [mych], [dbid])
#	ts3.requestClientKickFromChannel(schid, clientID, "Geblockter User")


#def onEditPlaybackVoiceDataEvent(self, schid, clientID, samples, channels):
#	ts3.printMessageToCurrentTab(str(channels))

class luemmelspluginpack(ts3plugin):

	#config
	name 				= "Luemmels Pluginpack"
	requestAutoload 	= False
	version 			= "1.0"
	apiVersion 			= 21
	author 				= "Luemmel"
	description 		= "Autokicker, Linkinfo, Autochannelgroup"
	offersConfigure		= True
	commandKeyword 		= "lu"
	infoTitle			= None	
	hotkeys 			= []
	dir					= path.join(getPluginPath(), "pyTSon", "scripts", "luemmelspluginpack")
	ini 				= path.join(dir, "config.ini")
	cfg 				= ConfigParser()
	ui 					= path.join(dir, "luemmelspluginpack.ui")
	
	#label
	enabled 			= "[color=green]aktiviert[/color]"
	disabled 			= "[color=red]deaktiviert[/color]"	
	l_autokick 			= "Automatischer kick nach Channel-Bann:"
	l_linkinfo 			= "Linkinfo:"
	l_friend_o 			= "Freunden automatisch Operator geben:"
	l_friend_tp 		= "Freunden automatisch Talkpower geben:"
	l_block_bankick 	= "Blockierten Usern Channel-Bann geben:"
	
	#messages
	m_block 			= "Ihhhhh ein geblockter User. Weg mit ihm!!! Bringt ihn zum Scheiterhaufen"
	m_bankick			= "Du wurdest mit einem Channel-Bann von mir oder von jemand anderem versehen. Ich habe dich in beiden Fällen gekickt."
	
	#On/Off Toggle
	t_autokick 			= False
	t_linkinfo 			= False
	t_friend_o 			= False
	t_friend_tp 		= False
	t_block_bankick 	= False
	
	#var
	gommeuid = "QTRtPmYiSKpMS8Oyd4hyztcvLqU="
	
	linkinfo_pre 		= ["http://", "https://", "http://www.", "https://www.", "www.", ""]
	linkinfo_domains 	= ["getlinkinfo.com", "9gag.com", "workupload.com", "amazon.com", "amazon.de", "youtube.com", "youtube.de", "google.com", "google.de", "facebook.com", "facebook.de", "twitch.tv"]
	
	
	menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "===============================", ""),
		(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 1, "=== Channel-Bann Autokick", ""), 
		(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 2, "On/Off", ""),
		(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 3, "=== Linkinfo", ""), 
		(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 4, "On/Off", ""),
		(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 5, "=== Freunde", ""), 
		(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 6, "On/Off Operator", ""),
		(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 7, "On/Off Talkpower", ""),
		(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 8, "=== Blockierte Spasten", ""), 
		(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 9, "On/Off Channel-Bann und Kick", ""),		
		(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 10, "===============================", "")]		

	def __init__(self):	
	
		self.dlg = None	
		
		#Check dir
		if not os.path.exists(self.dir):os.makedirs(self.dir)
		
		#Check ini
		if path.isfile(self.ini):self.cfg.read(self.ini)
		else:
			self.cfg['toggle'] = { "autokick": "True", "linkinfo": "True", "friend_o": "True", "friend_tp": "True", "block_bankick": "True" }
			with open(self.ini, 'w') as configfile:
				self.cfg.write(configfile)
				
		self.t_autokick 		= self.cfg.getboolean('toggle','autokick')
		self.t_linkinfo 		= self.cfg.getboolean('toggle','linkinfo')
		self.t_friend_o 		= self.cfg.getboolean('toggle','friend_o')
		self.t_friend_tp 		= self.cfg.getboolean('toggle','friend_tp')
		self.t_block_bankick 	= self.cfg.getboolean('toggle','block_bankick')
		
		#Database connect
		self.db = QSqlDatabase.addDatabase("QSQLITE","pyTSon_contacts")
		self.db.setDatabaseName(ts3.getConfigPath() + "settings.db")

		if not self.db.isValid():raise Exception("Datenbank ungültig")
		if not self.db.open():raise Exception("Datenbank konnte nicht geöffnet werden")	
		
		#init statusmessage
		ts3.printMessageToCurrentTab("\n[color=orange]"+self.name+"[/color]")		
		
		if self.t_autokick:ts3.printMessageToCurrentTab(self.l_autokick+" "+self.enabled)					
		else:ts3.printMessageToCurrentTab(self.l_autokick+" "+self.disabled)
		if self.t_linkinfo:ts3.printMessageToCurrentTab(self.l_linkinfo+" "+self.enabled)
		else:ts3.printMessageToCurrentTab(self.l_linkinfo+" "+self.disabled)
		if self.t_friend_o:ts3.printMessageToCurrentTab(self.l_friend_o+" "+self.enabled)
		else:ts3.printMessageToCurrentTab(self.l_friend_o+" "+self.disabled)
		if self.t_friend_tp:ts3.printMessageToCurrentTab(self.l_friend_tp+" "+self.enabled)
		else:ts3.printMessageToCurrentTab(self.l_friend_tp+" "+self.disabled)
		if self.t_block_bankick:ts3.printMessageToCurrentTab(self.l_block_bankick+" "+self.enabled)
		else:ts3.printMessageToCurrentTab(self.l_block_bankick+" "+self.disabled)		
	
	def stop(self):		
		self.db.close();self.db.delete()
		QSqlDatabase.removeDatabase("pyTSon_contacts")	
		ts3.printMessageToCurrentTab("\n[color=orange]"+self.name+"[/color] wurde "+self.disabled)	

	def processCommand(self, schid, command):    
		if command == "kickall":
			(error, myid) = ts3.getClientID(schid)
			(error, mych) = ts3.getChannelOfClient(schid, myid)			
			(error, clist) = ts3.getChannelClientList(schid, mych)			
			for client in clist:
				(error, gid) = ts3.getClientVariableAsInt(schid, client, ts3defines.ClientPropertiesRare.CLIENT_CHANNEL_GROUP_ID)
				if not gid == 10 or not gid == 11:
					ts3.requestClientKickFromChannel(schid, client, "Nicht nur du :P")		
					time.sleep( 1 )				
			return True
		if command == "gui":
			if not self.dlg:
				self.dlg = SettingsDialog(self)
			self.dlg.show()
			self.dlg.raise_()
			self.dlg.activateWindow()
			return True
		if command == "host":
			(error, banner) = ts3.getServerVariableAsString(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_HOSTBANNER_GFX_URL)
			ts3.printMessageToCurrentTab(banner)
			return True
			
	def contactStatus(self, uid):
		q = self.db.exec_("SELECT * FROM contacts WHERE value LIKE '%%IDS=%s%%'" % uid)
		ret = 2
		if q.next():
			val = q.value("value")
			for l in val.split('\n'):
				if l.startswith('Friend='):ret = int(l[-1])
		q.delete();return ret				

	def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
		if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL:
			if menuItemID == 2:					
				self.t_autokick = not self.t_autokick
				self.cfg.set('toggle', 'autokick', str(self.t_autokick))
				if self.t_autokick:ts3.printMessageToCurrentTab(self.l_autokick+" "+self.enabled)					
				else:ts3.printMessageToCurrentTab(self.l_autokick+" "+self.disabled)							
			if menuItemID == 4:				
				self.t_linkinfo = not self.t_linkinfo
				self.cfg.set('toggle', 'linkinfo', str(self.t_linkinfo))
				if self.t_linkinfo:ts3.printMessageToCurrentTab(self.l_linkinfo+" "+self.enabled)
				else:ts3.printMessageToCurrentTab(self.l_linkinfo+" "+self.disabled)
			if menuItemID == 6:				
				self.t_friend_o = not self.t_friend_o
				self.cfg.set('toggle', 'friend_o', str(self.t_friend_o))
				if self.t_friend_o:ts3.printMessageToCurrentTab(self.l_friend_o+" "+self.enabled)
				else:ts3.printMessageToCurrentTab(self.l_friend_o+" "+self.disabled)
			if menuItemID == 7:				
				self.t_friend_tp = not self.t_friend_tp
				self.cfg.set('toggle', 'friend_tp', str(self.t_friend_tp))
				if self.t_friend_tp:ts3.printMessageToCurrentTab(self.l_friend_tp+" "+self.enabled)
				else:ts3.printMessageToCurrentTab(self.l_friend_tp+" "+self.disabled)			
			if menuItemID == 9:				
				self.t_block_bankick = not self.t_block_bankick
				self.cfg.set('toggle', 'block_bankick', str(self.t_block_bankick))
				if self.t_block_bankick:ts3.printMessageToCurrentTab(self.l_block_bankick+" "+self.enabled)
				else:ts3.printMessageToCurrentTab(self.l_block_bankick+" "+self.disabled)
				
			with open(self.ini, 'w') as configfile:
				self.cfg.write(configfile)
				
				
	def onClientMoveEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moveMessage):
		#ServerUID abfragen
		(error, suid) = ts3.getServerVariableAsString(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
		
		#Wenn ServerUID von Gomme und wenn Freunde oder Blockierte Funktion aktiviert
		if suid == self.gommeuid and (self.t_friend_o == True or self.t_friend_tp == True or self.t_block_bankick == True):
			
			#Meine Client und ChannelID
			(error, myid) = ts3.getClientID(schid)
			(error, mych) = ts3.getChannelOfClient(schid, myid)	
			
			#Wenn User in mein Cahnnel joint
			if newChannelID == mych:
			
				#UID des Users abfragen
				(error, uid) = ts3.getClientVariableAsString(schid, clientID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
				
				#Freundschaftsstatus des Users abfragen
				f = self.contactStatus(uid)
				
				#Aktuelle Channelgruppe des gejointen Users abfragen
				(error, gid) = ts3.getClientVariableAsInt(schid, clientID, ts3defines.ClientPropertiesRare.CLIENT_CHANNEL_GROUP_ID)
				
				#Meine aktuelle Channelgruppe abfragen
				(error, mygid) = ts3.getClientVariableAsInt(schid, myid, ts3defines.ClientPropertiesRare.CLIENT_CHANNEL_GROUP_ID)
				(error, name) = ts3.getClientVariableAsInt(schid, myid, ts3defines.ClientProperties.CLIENT_NICKNAME)
				# Block Ban Kick
				if f == 1 and self.t_block_bankick == True and (mygid == 10 or mygid == 11):					
					(error, dbid) = ts3.getClientVariableAsUInt64(schid, clientID, ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
					ts3.requestSetClientChannelGroup(schid, [12], [mych], [dbid])
					ts3.requestClientKickFromChannel(schid, clientID, "Geblockter User")
					ts3.requestSendPrivateTextMsg(schid, self.m_block, clientID)
			
				# Freund O
				if f == 0 and self.t_friend_o == True and mygid == 10 and not gid == 11:
					(error, dbid) = ts3.getClientVariableAsUInt64(schid, clientID, ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
					ts3.requestSetClientChannelGroup(schid, [11], [mych], [dbid])

				# Freund TP 
				if f == 0 and self.t_friend_tp == True and mygid == 11:	
					(error, tp) = ts3.getChannelVariableAsInt(schid, mych, ts3defines.ChannelPropertiesRare.CHANNEL_NEEDED_TALK_POWER)
					if tp > 3:ts3.requestClientSetIsTalker(schid, clientID, True)
				
				if name == "Götzenbild_":
					(error, dbid) = ts3.getClientVariableAsUInt64(schid, clientID, ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
					ts3.requestSetClientChannelGroup(schid, [12], [mych], [dbid])
					ts3.requestClientKickFromChannel(schid, clientID, "Geblockter User")


	def onClientChannelGroupChangedEvent(self, schid, channelGroupID, channelID, clientID, invokerClientID, invokerName, invokerUniqueIdentity):
		#ServerUID abfragen		
		(error, suid) = ts3.getServerVariableAsString(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
		
		#Wenn autokick aktiviert und ServerUID von Gomme		
		if self.t_autokick == True and suid == self.gommeuid:
			
			#Meine ClientID und ChannelID
			(error, myid) = ts3.getClientID(schid)
			(error, mych) = ts3.getChannelOfClient(schid, myid)		
			
			#Meine aktuelle Channelgruppe abfragen
			(error, mygid) = ts3.getClientVariableAsInt(schid, myid, ts3defines.ClientPropertiesRare.CLIENT_CHANNEL_GROUP_ID)


			#Wenn in meinem Channel ein Channel-Bann verteilt wurde und ich O oder C bin 
			if mych == channelID and channelGroupID == 12 and (mygid == 10 or mygid == 11):
				
				#Client kicken und nette Nachricht senden
				ts3.requestClientKickFromChannel(schid, clientID, "Geblockter User")
				ts3.requestSendPrivateTextMsg(schid, self.m_bankick, clientID)


	def onTextMessageEvent(self, schid, targetMode, toID, fromID, fromName, fromUniqueIdentifier, message, ffIgnored):
		if self.t_linkinfo == True:
			(error, myid) = ts3.getClientID(schid)
			
			message = message.lower()		
			
			#if url in message
			if not myid == fromID and ("[url]" in message or "[url=" in message):			
				#check url
				found_domain = False		
				for domain in self.linkinfo_domains:
					for pre in self.linkinfo_pre:
						if "[url]"+pre+domain in message or "[url="+pre+domain in message:found_domain = True		
				if "steam://" in message or "client://" in message or "ts3server://" in message:found_domain = True					
				
				#if url not whitelisted
				if found_domain == False:
					start = message.find("[url]")				
					if not start == -1:
						end = message.find("[/url]")			
						message = message[start+5:end]							
					else:
						start = message.find("[url=")						
						end = message.find("]")						
						message = message[start+5:end]				

					message = message+" -> [url=http://www.getlinkinfo.com/info?link="+message+"]Linkinfo[/url]"			
					
					if targetMode == 1:ts3.requestSendPrivateTextMsg(schid, message, fromID)
					if targetMode == 2:
						(error, mych) = ts3.getChannelOfClient(schid, myid)	
						ts3.requestSendChannelTextMsg(schid, message, mych)
						

class SettingsDialog(QDialog):
	def __init__(self,info, parent=None):
		super(QDialog, self).__init__(parent)
		setupUi(self, os.path.join(ts3.getPluginPath(), "pyTSon", "scripts", "luemmelspluginpack", "luemmelspluginpack.ui"), [("QWidget", True, [])])
		self.setWindowTitle("Extended Info Settings")

			
			
			