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

from qgis.core import *
from qgis.gui import *

from .ui.mapfileexportdlg_ui import Ui_MapfileExportDlg

import MapfileExporter
import utils
from utils import toUTF8

class MapfileExportDlg(QDialog, Ui_MapfileExportDlg):


    def __init__(self, iface, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.legend = self.iface.legendInterface()

        # hide map unit combo and label
        self.label4.hide()
        self.cmbMapUnits.hide()

        # setup the template table
        m = TemplateModel(self)
        for layer in self.legend.layers():
            m.append( layer )
        self.templateTable.setModel(m)
        d = TemplateDelegate(self)
        self.templateTable.setItemDelegate(d)

        # get the default title from the project
        title = QgsProject.instance().title()
        if title == "":
            title = QFileInfo( QgsProject.instance().fileName() ).completeBaseName()
        if title != "":
            self.txtMapName.setText( title )

        # fill the image format combo
        self.cmbMapImageType.addItems( ["png", "gif", "jpeg", "svg", "GTiff"] )

        QObject.connect( self.btnChooseFile, SIGNAL("clicked()"), self.selectMapFile )
        QObject.connect( self.btnChooseTemplate, SIGNAL("clicked()"), self.selectTemplateBody )
        QObject.connect( self.btnChooseTmplHeader, SIGNAL("clicked()"), self.selectTemplateHeader )
        QObject.connect( self.btnChooseTmplFooter, SIGNAL("clicked()"), self.selectTemplateFooter )

    def selectMapFile(self):
        # retrieve the last used map file path
        settings = QSettings()
        lastUsedFile = settings.value("/rt_mapserver_exporter/lastUsedFile", "", type=str)

        # ask for choosing where to store the map file
        filename = QFileDialog.getSaveFileName(self, "Select where to save the map file", lastUsedFile, "MapFile (*.map)")
        if filename == "":
            return

        # store the last used map file path
        settings.setValue("/rt_mapserver_exporter/lastUsedFile", filename)
        # update the displayd path
        self.txtMapFilePath.setText( filename )

    def selectTemplateBody(self):
        self.selectTemplateFile( self.txtTemplatePath )

    def selectTemplateHeader(self):
        self.selectTemplateFile( self.txtTmplHeaderPath )

    def selectTemplateFooter(self):
        self.selectTemplateFile( self.txtTmplFooterPath )

    def selectTemplateFile(self, lineedit):
        # retrieve the last used template file path
        settings = QSettings()
        lastUsedFile = settings.value("/rt_mapserver_exporter/lastUsedTmpl", "", type=str)

        # ask for choosing where to store the map file
        filename = QFileDialog.getOpenFileName(self, "Select the template file", lastUsedFile, "Template (*.html *.tmpl);;All files (*);;")
        if filename == "":
            return

        # store the last used map file path
        settings.setValue("/rt_mapserver_exporter/lastUsedTmpl", filename)
        # update the path
        lineedit.setText( filename )


    def accept(self):
        # check user inputs
        if self.txtMapFilePath.text() == "":
            QMessageBox.warning(self, "RT MapServer Exporter", "Mapfile output path is required")

        else:
            units = utils.unitMap[self.canvas.mapUnits()]
            if self.cmbMapUnits.currentIndex() >= 0:
                u, result = self.cmbMapUnits.itemData(self.cmbMapUnits.currentIndex())
                if result:
                    units = u
            
            MapfileExporter.export(
                name = toUTF8(self.txtMapName.text()),
                width = int(self.txtMapWidth.text()),
                height = int(self.txtMapHeight.text()),
                units = units,
                extent = self.canvas.fullExtent(),
                projection = toUTF8(self.canvas.mapRenderer().destinationCrs().toProj4()),
                shapePath = toUTF8(self.txtMapShapePath.text()),
                backgroundColor = self.canvas.canvasColor(),
                imageType = toUTF8(self.cmbMapImageType.currentText()),
                imagePath = toUTF8(self.getWebImagePath()),
                imageURL = toUTF8(self.getWebImageUrl()),
                tempPath = toUTF8(self.getWebTemporaryPath()),
                validationRegexp =  toUTF8(self.getExternalGraphicRegexp()),
                templatePath = toUTF8(self.getTemplatePath()),
                templateHeaderPath = toUTF8(self.getTemplateHeaderPath()),
                templateFooterPath = toUTF8(self.getTemplateFooterPath()),
                mapServerURL = toUTF8(self.txtMapServerUrl.text()),
                mapfilePath = toUTF8(self.txtMapFilePath.text()),
                createFontFile = self.checkCreateFontFile.isChecked(),
                fontsetPath = self.txtMapFontsetPath.text(), 

                layers = self.legend.layers(),
                legend = self.legend
            )

            QDialog.accept(self)

    def generateTemplate(self):
        tmpl = u""

        if self.getTemplateHeaderPath() == "":
            tmpl += u'''<!-- MapServer Template -->
    <html>
    <head>
    <title>%s</title>
    </head>
    <body>
    ''' % self.txtMapName.text()

        for lid, orientation in self.templateTable.model().getObjectIter():
            layer = QgsMapLayerRegistry.instance().mapLayer(lid)
            if not layer:
                continue

            # define the template file content
            tmpl += '[resultset layer="%s"]\n' % layer.id()

            layerTitle = layer.title() if layer.title() != "" else layer.name()
            tmpl += u'<b>"%s"</b>\n' % layerTitle

            tmpl += '<table class="idtmplt_tableclass">\n'

            if orientation == Qt.Horizontal:
                tmpl += '  <tr class="idtmplt_trclass_1h">\n'
                for idx, fld in enumerate(layer.dataProvider().fields()):
                    fldDescr = fld.comment() if fld.comment() != "" else fld.name()
                    tmpl += u'    <td class="idtmplt_tdclass_1h">"%s"</td>\n' % fldDescr
                tmpl += '</tr>\n'

                tmpl += '[feature limit=20]\n'

                tmpl += '  <tr class="idtmplt_trclass_2h">\n'
                for idx, fld in enumerate(layer.dataProvider().fields()):
                    fldDescr = fld.comment() if fld.comment() != "" else fld.name()
                    tmpl += u'    <td class="idtmplt_tdclass_2h">[item name="%s"]</td>\n' % fld.name()
                tmpl += '  </tr>\n'

                tmpl += '[/feature]\n'

            else:
                for idx, fld in enumerate(layer.dataProvider().fields()):
                    tmpl += '  <tr class="idtmplt_trclass_v">\n'

                    fldDescr = fld.comment() if fld.comment() != "" else fld.name()
                    tmpl += u'    <td class="idtmplt_tdclass_1v">"%s"</td>\n' % fldDescr

                    tmpl += '[feature limit=20]\n'
                    tmpl += u'    <td class="idtmplt_tdclass_2v">[item name="%s"]</td>\n' % fld.name()
                    tmpl += '[/feature]\n'

                    tmpl += '  </tr>\n'

            tmpl += '</table>\n'

            tmpl += '[/resultset]\n'
            tmpl += '<hr>\n'


        if self.getTemplateFooterPath() == "":
            tmpl += '''  </body>
    </html>'''

        return tmpl

    def getTemplatePath(self):
        if self.checkTmplFromFile.isChecked():
            return self.txtTemplatePath.text() # "[templatepath]"

        elif self.checkGenerateTmpl.isChecked():
            # generate the template for layers
            tmplContent = self.generateTemplate()
            # store the template alongside the mapfile
            tmplPath = self.txtMapFilePath.text() + ".html.tmpl"
            with open(unicode(tmplPath), 'w') as fout:
                fout.write(tmplContent)
            return tmplPath

    def getTemplateHeaderPath(self):
        return self.txtTmplHeaderPath.text()

    def getTemplateFooterPath(self):
        return self.txtTmplFooterPath.text()


    def getMapShapePath(self):
        return self.txtMapShapePath.text()


    def getWebImagePath(self):
        return self.txtWebImagePath.text() #"/tmp/"

    def getWebImageUrl(self):
        return self.txtWebImageUrl.text() #"/tmp/"

    def getWebTemporaryPath(self):
        return self.txtWebTempPath.text() #"/tmp/"

    def getExternalGraphicRegexp(self):
        return self.txtExternalGraphicRegexp.text()
class TemplateDelegate(QItemDelegate):
    """ delegate with some special item editors """

    def createEditor(self, parent, option, index):
        # special combobox for orientation
        if index.column() == 1:
            cbo = QComboBox(parent)
            cbo.setEditable(False)
            cbo.setFrame(False)
            for val, txt in enumerate(TemplateModel.ORIENTATIONS):
                cbo.addItem(txt, val)
            return cbo
        return QItemDelegate.createEditor(self, parent, option, index)

    def setEditorData(self, editor, index):
        """ load data from model to editor """
        m = index.model()
        if index.column() == 1:
            val = m.data(index, Qt.UserRole)[0]
            editor.setCurrentIndex( editor.findData(val) )
        else:
            # use default
            QItemDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        """ save data from editor back to model """
        if index.column() == 1:
            val = editor.itemData(editor.currentIndex())[0]
            model.setData(index, TemplateModel.ORIENTATIONS[val])
            model.setData(index, val, Qt.UserRole)
        else:
            # use default
            QItemDelegate.setModelData(self, editor, model, index)

class TemplateModel(QStandardItemModel):

    ORIENTATIONS = { Qt.Horizontal : u"Horizontal", Qt.Vertical : u"Vertical" }

    def __init__(self, parent=None):
        self.header = ["Layer name", "Orientation"]
        QStandardItemModel.__init__(self, 0, len(self.header), parent)

    def append(self, layer):
        rowdata = []

        item = QStandardItem( unicode(layer.name()) )
        item.setFlags( item.flags() & ~Qt.ItemIsEditable )
        rowdata.append( item )

        item = QStandardItem( TemplateModel.ORIENTATIONS[Qt.Horizontal] )
        item.setFlags( item.flags() | Qt.ItemIsEditable )
        rowdata.append( item )

        self.appendRow( rowdata )

        row = self.rowCount()-1
        self.setData(self.index(row, 0), layer.id(), Qt.UserRole)
        self.setData(self.index(row, 1), Qt.Horizontal, Qt.UserRole)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[section]
        return None

    def getObject(self, row):
        lid = self.data(self.index(row, 0), Qt.UserRole)
        orientation = self.data(self.index(row, 1), Qt.UserRole)
        return (lid, orientation)

    def getObjectIter(self):
        for row in range(self.rowCount()):
            yield self.getObject(row)

