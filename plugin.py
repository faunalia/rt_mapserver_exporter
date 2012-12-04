# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name                 : RT MapServer Exporter
Description          : A plugin to export qgs project to mapfile
Date                 : Oct 21, 2012 
copyright            : (C) 2012 by Giuseppe Sucameli (Faunalia)
email                : brush.tyler@gmail.com

 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class Plugin:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        self.action = QAction(QIcon(":/plugins/RT_MapServer_Exporter/logo"), "Export project to mapfile", self.iface.mainWindow())
        QObject.connect(self.action, SIGNAL("triggered()"), self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("RT MapServer Exporter", self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        self.iface.removePluginMenu("RT MapServer Exporter", self.action)
        self.action = None

    def run(self):
        from .mapfileexportdlg import MapfileExportDlg
        dialog = MapfileExportDlg(self.iface, self.iface.mainWindow())
        dialog.show()
        dialog.exec_()
