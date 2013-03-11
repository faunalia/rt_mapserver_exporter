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

def name():
	return "RT MapServer Exporter"

def description():
	return "Export QGIS project to MapFile. Developed with funding from Regione Toscana-SITA."

def author():
	return "Giuseppe Sucameli (Faunalia)"

def icon():
	return "icons/logo.png"

def version():
	return "0.2.1"

def qgisMinimumVersion():
	return "1.9"

def classFactory(iface):
	from .plugin import Plugin
	return Plugin(iface)

