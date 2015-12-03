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

import resources_rc

class Plugin:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        self.action = QAction(QIcon(":/rt_mapserver_exporter/icons/logo"), "Export project to mapfile", self.iface.mainWindow())
        QObject.connect(self.action, SIGNAL("triggered()"), self.run)

        self.aboutAction = QAction( QIcon( ":/rt_mapserver_exporter/icons/about" ), "About", self.iface.mainWindow() )
        QObject.connect( self.aboutAction, SIGNAL("triggered()"), self.about )

        if hasattr(self.iface, "addPluginToWebMenu"):
            self.iface.addWebToolBarIcon(self.action)
            self.iface.addPluginToWebMenu("RT MapServer Exporter", self.action)
            self.iface.addPluginToWebMenu("RT MapServer Exporter", self.aboutAction)
        else:
            self.iface.addToolBarIcon(self.action)
            self.iface.addPluginToMenu("RT MapServer Exporter", self.action)
            self.iface.addPluginToMenu("RT MapServer Exporter", self.aboutAction)

    def unload(self):
        if hasattr(self.iface, "removePluginWebMenu"):
            self.iface.removeWebToolBarIcon(self.action)
            self.iface.removePluginWebMenu("RT MapServer Exporter", self.action)
            self.iface.removePluginWebMenu("RT MapServer Exporter", self.aboutAction)
        else:
            self.iface.removeToolBarIcon(self.action)
            self.iface.removePluginMenu("RT MapServer Exporter", self.action)
            self.iface.removePluginMenu("RT MapServer Exporter", self.aboutAction)

    def about(self):
        """ display the about dialog """
        from .DlgAbout import DlgAbout
        dlg = DlgAbout( self.iface.mainWindow() )
        dlg.exec_()

    def run(self):
        try:
            import mapscript
            from .mapfileexportdlg import MapfileExportDlg
            dialog = MapfileExportDlg(self.iface, self.iface.mainWindow())
            dialog.show()
            dialog.exec_()
        except ImportError:
            QMessageBox.warning(None, "Import Error", "Missing module: 'mapscript'. Please install 'mapscript-python' first.")
