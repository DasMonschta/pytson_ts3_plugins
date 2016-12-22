from ts3plugin import ts3plugin, PluginHost
from ts3 import getPluginPath
from os import path
import ts3, ts3defines, os.path,  pickle

from PythonQt.QtGui import *
from PythonQt.QtCore import Qt
from pytsonui import *

class Blacklist(ts3plugin):
    name				= "Blacklist"
    requestAutoload		= False
    version				= "1.0"
    apiVersion			= 21
    author				= "Luemmel"
    description			= "Blacklist nicknames. Type \"/py bl help\" for more information."
    offersConfigure		= True
    commandKeyword		= "bl"
    infoTitle			= None
    hotkeys				= []
    directory			= path.join(getPluginPath(), "pyTSon", "scripts", "blacklist")
    txt					= path.join(directory, "config.txt")
    bl 					= []
    gomme_uid           = "QTRtPmYiSKpMS8Oyd4hyztcvLqU="

    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 0, "Add nickname to blacklist", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 1, "Remove nickname form blacklist", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 2, "Show blacklist", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 3, "Help", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Blacklist GUI", "")]

    def __init__(self):
        self.dlg = None
        if not os.path.exists(self.directory):os.makedirs(self.directory)
        if path.isfile(self.txt):
            with open (self.txt, 'rb') as fp:self.bl = pickle.load(fp)
        else:
            with open(self.txt, 'wb') as fp:pickle.dump([], fp)

    def bl_txt_update(self):
        with open(self.txt, 'wb') as fp:pickle.dump(self.bl, fp)

    def bl_add(self, nickname):
        nickname_low = nickname.lower()
        if not nickname_low in self.bl:
            self.bl.append(nickname_low)
            self.bl = sorted(self.bl)
            self.bl_txt_update()
            ts3.printMessageToCurrentTab("\""+nickname+"\" is [b]now[/b] blacklisted.")
        else:ts3.printMessageToCurrentTab("\""+nickname+"\" is [b]already[/b] blacklisted.")

    def bl_remove(self, nickname):
        nickname_low = nickname.lower()
        if nickname_low in self.bl:
            self.bl.remove(nickname_low)
            self.bl_txt_update()
            ts3.printMessageToCurrentTab("\""+nickname+"\" is [b]no longer[/b] blacklisted.")
        else:ts3.printMessageToCurrentTab("\""+nickname+"\" is [b]not[/b] blacklisted.")

    def bl_show(self):
        if len(self.bl) > 0:
            ts3.printMessageToCurrentTab("--- Balcklist ---")
            for nick in self.bl:ts3.printMessageToCurrentTab(nick)
            ts3.printMessageToCurrentTab("-----------------")
        else:ts3.printMessageToCurrentTab("Blacklist is [b]empty[/b].")

    def open_dlg(self):
        if not self.dlg:
            self.dlg = SettingsDialog(self)
        self.dlg.show()
        self.dlg.raise_()
        self.dlg.activateWindow()
        return True

    @staticmethod
    def help():
        ts3.printMessageToCurrentTab("Keyword: bl - /py bl [parameter] [optional nickname]")
        ts3.printMessageToCurrentTab("add NICKNAME - add a nickname to the blacklist")
        ts3.printMessageToCurrentTab("remove NICKNAME - remove a blacklisted nickname")
        ts3.printMessageToCurrentTab("show - print the blacklist to the current tab")
        ts3.printMessageToCurrentTab("gui - open the GUI")
        ts3.printMessageToCurrentTab("help - you are here. you know what will happen :P")

    def onMenuItemEvent(self, sch_id, a_type, menu_item_id, selected_item_id):
        if a_type == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT:
            (error, nickname) = ts3.getClientVariableAsString(sch_id, selected_item_id, ts3defines.ClientProperties.CLIENT_NICKNAME)
            if menu_item_id == 0:self.bl_add(nickname)
            if menu_item_id == 1:self.bl_remove(nickname)
            if menu_item_id == 2:self.bl_show()
            if menu_item_id == 3:self.help()
        elif a_type == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL:
            if menu_item_id == 0: self.open_dlg()

    def processCommand(self, sch_id, command):
        com = command.split(" ", 1)
        if len(com) == 2:
            if com[0] == "add":self.bl_add(com[1]);return True
            if com[0] == "remove":self.bl_remove(com[1]);return True
        if com[0] == "show":self.bl_show();return True
        if com[0] == "help":self.help();return True
        if com[0] == "gui":self.open_dlg();return True


    def onClientMoveEvent(self, sch_id, user_id, old_channel_id, new_channel_id, visibility, move_message):
        (error, cl_id) = ts3.getClientID(sch_id)
        (error, cl_ch) = ts3.getChannelOfClient(sch_id, cl_id)

        if new_channel_id == cl_ch and not user_id == cl_id:
            (error, nickname) = ts3.getClientVariableAsString(sch_id, user_id, ts3defines.ClientProperties.CLIENT_NICKNAME)
            nickname = nickname.lower()
            for nick in self.bl:
                if nick in nickname:
                    (error, suid) = ts3.getServerVariableAsString(sch_id, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
                    if suid == self.gomme_uid:
                        (error, dbid) = ts3.getClientVariableAsUInt64(sch_id, user_id, ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
                        ts3.requestSetClientChannelGroup(sch_id, [12], [cl_ch], [dbid])
                    else:
                        ts3.requestClientKickFromChannel(sch_id, user_id, "Blacklisted name.")

class SettingsDialog(QDialog):
    def __init__(self, blacklist, parent=None):
        self.bl = blacklist
        super(QDialog, self).__init__(parent)
        setupUi(self, os.path.join(ts3.getPluginPath(), "pyTSon", "ressources", "blacklist", "blacklist.ui"))
        self.setWindowTitle("Blacklist by Luemmel")
        self.btn_add.clicked.connect(self.showadd)
        self.btn_remove.clicked.connect(self.showremove)
        self.list.addItems(blacklist.bl)

    def showadd(self):
        text = self.input_text.toPlainText()
        self.bl.bl_add(text)
        self.list.clear()
        self.list.addItems(self.bl.bl)

    def showremove(self):
        selected_item = self.list.currentItem().text()
        self.bl.bl_remove(selected_item)
        self.list.clear()
        self.list.addItems(self.bl.bl)
