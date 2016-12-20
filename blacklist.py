from ts3plugin import ts3plugin, PluginHost
from ts3 import getPluginPath
from os import path
import ts3, ts3defines, os.path,  pickle	
	
class blacklist(ts3plugin):
	name 				= "Blacklist"
	requestAutoload 	= False
	version 			= "1.0"
	apiVersion 			= 21
	author 				= "Luemmel"
	description 		= "Blacklist nicknames."
	offersConfigure		= True
	commandKeyword 		= "bl"
	infoTitle			= None	
	hotkeys 			= []	
	dir					= path.join(getPluginPath(), "pyTSon", "scripts", "namekick")
	txt 				= path.join(dir, "config.txt")
	
	menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 0, "Add nickname to blacklist", ""),
		(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 1, "Remove nickname form blacklist", ""),
		(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 2, "Show blacklist", ""),
		(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 3, "Help", "")]		

	def __init__(self):			
		if not os.path.exists(self.dir):os.makedirs(self.dir)
		if not path.isfile(self.txt):	
			with open(self.txt, 'wb') as fp:pickle.dump([], fp)
	
	def read_txt():
		with open (self.txt, 'rb') as fp:read_bl = pickle.load(fp)	
		return read_bl
		
	def bl_add(self, nickname_low, nickname):
		with open (self.txt, 'rb') as fp:read_bl = pickle.load(fp)			
		if not nickname_low in read_bl:			
			read_bl.append(nickname_low)
			with open(self.txt, 'wb') as fp:pickle.dump(read_bl, fp)
			ts3.printMessageToCurrentTab("\""+nickname+"\" is [b]now[/b] blacklisted.")						
		else:ts3.printMessageToCurrentTab("\""+nickname+"\" is [b]already[/b] blacklisted.")				

	def bl_remove(self, nickname_low, nickname):
		with open (self.txt, 'rb') as fp:read_bl = pickle.load(fp)			
		if nickname_low in read_bl:			
			read_bl.remove(nickname_low)
			with open(self.txt, 'wb') as fp:pickle.dump(read_bl, fp)	
			ts3.printMessageToCurrentTab("\""+nickname+"\" is [b]no longer[/b] blacklisted.")
		else:ts3.printMessageToCurrentTab("\""+nickname+"\" is [b]not[/b] blacklisted.")			

	def bl_show(self):
		with open (self.txt, 'rb') as fp:read_bl = pickle.load(fp)			
		if len(read_bl) > 0:			
			ts3.printMessageToCurrentTab("--- Balcklist ---")	
			for nick in read_bl:ts3.printMessageToCurrentTab(nick)
			ts3.printMessageToCurrentTab("-----------------")		
		else:ts3.printMessageToCurrentTab("Blacklist is [b]empty[/b].")					
		
	def help(self):		
		ts3.printMessageToCurrentTab("Keyword: bl - /py bl [parameter] [optional nickname]")	
		ts3.printMessageToCurrentTab("add NICKNAME - add a nickname to the blacklist")	
		ts3.printMessageToCurrentTab("remove NICKNAME - remove a blacklisted nickname")	
		ts3.printMessageToCurrentTab("show - print the blacklist to the current tab")	
		ts3.printMessageToCurrentTab("help - you are here. you know what will happen :P")
		
	def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
		if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT:
			(error, nickname) = ts3.getClientVariableAsString(schid, selectedItemID, ts3defines.ClientProperties.CLIENT_NICKNAME)				
			nickname_low = nickname.lower()			
			if menuItemID == 0:self.bl_add(nickname_low, nickname)		
			if menuItemID == 1:self.bl_remove(nickname_low, nickname)	
			if menuItemID == 2:self.bl_show()
			if menuItemID == 3:self.help()
				
	def processCommand(self, schid, command):			
		com = command.split(" ", 1)
		if len(com) == 2:
			nickname_low = com[1].lower()		
			if com[0] == "add":self.bl_add(nickname_low, com[1]);return True			
			if com[0] == "remove":self.bl_remove(nickname_low, com[1]);return True	
		if com[0] == "show":self.bl_show();return True
		if com[0] == "help":self.help();return True
	
	def onClientMoveEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moveMessage):
		(error, myid) = ts3.getClientID(schid)
		(error, mych) = ts3.getChannelOfClient(schid, myid)	

		if newChannelID == mych:
			(error, nickname) = ts3.getClientVariableAsString(schid, clientID, ts3defines.ClientProperties.CLIENT_NICKNAME)		
			nickname = nickname.lower()	
			with open (self.txt, 'rb') as fp:read_bl = pickle.load(fp)	
			if nickname in read_bl:ts3.requestClientKickFromChannel(schid, clientID, "Blacklisted name.")	
	
