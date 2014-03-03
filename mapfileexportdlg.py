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
import mapscript
import re

_toUtf8 = lambda s: unicode(s).encode('utf8')


class MapfileExportDlg(QDialog, Ui_MapfileExportDlg):

    unitMap = {
        QGis.DecimalDegrees : mapscript.MS_DD,
        QGis.Meters : mapscript.MS_METERS,
        QGis.Feet : mapscript.MS_FEET
    }

    onOffMap = {
        True : mapscript.MS_ON,
        False : mapscript.MS_OFF
    }

    trueFalseMap = {
        True : mapscript.MS_TRUE,
        False : mapscript.MS_FALSE
    }

    @classmethod
    def getLayerType(self, layer):
        if layer.type() == QgsMapLayer.RasterLayer:
            return mapscript.MS_LAYER_RASTER
        if layer.geometryType() == QGis.Point:
            return mapscript.MS_LAYER_POINT
        if layer.geometryType() == QGis.Line:
            return mapscript.MS_LAYER_LINE
        if layer.geometryType() == QGis.Polygon:
            return mapscript.MS_LAYER_POLYGON

    @classmethod
    def getLabelPosition(self, palLabel):
        quadrantPosition = palLabel.quadOffset  
        if quadrantPosition == QgsPalLayerSettings.QuadrantAboveLeft: # y=1 x=-1 
            return mapscript.MS_UL
        if quadrantPosition == QgsPalLayerSettings.QuadrantAbove: # y=1 x=0
            return mapscript.MS_UC
        if quadrantPosition == QgsPalLayerSettings.QuadrantAboveRight: # y=1 x=1
            return mapscript.MS_UR
        if quadrantPosition == QgsPalLayerSettings.QuadrantLeft: # y=0 x=-1
            return mapscript.MS_CL
        if quadrantPosition == QgsPalLayerSettings.QuadrantOver: # y=0 x=0
            return mapscript.MS_CC
        if quadrantPosition == QgsPalLayerSettings.QuadrantRight: # y=0 x=1
            return mapscript.MS_CR
        if quadrantPosition == QgsPalLayerSettings.QuadrantBelowLeft: # y=-1 x=-1 
            return mapscript.MS_LL
        if quadrantPosition == QgsPalLayerSettings.QuadrantBelow: # y=-1 x=0
            return mapscript.MS_LC
        if quadrantPosition == QgsPalLayerSettings.QuadrantBelowRight: # y=-1 x=1
            return mapscript.MS_LR
        return mapscript.MS_AUTO

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
            return

        # create a new ms_map
        ms_map = mapscript.mapObj()
        ms_map.name = _toUtf8( self.txtMapName.text() )

        # map size
        width, height = int(self.txtMapWidth.text()), int(self.txtMapHeight.text())
        widthOk, heightOk = isinstance(width, int), isinstance(height, int)
        if widthOk and heightOk:
            ms_map.setSize( width, height )

        # map units
        ms_map.units = self.unitMap[ self.canvas.mapUnits() ]
        if self.cmbMapUnits.currentIndex() >= 0:
            units, ok = self.cmbMapUnits.itemData( self.cmbMapUnits.currentIndex() )
            if ok:
                ms_map.units = units

        # map extent
        extent = self.canvas.fullExtent()
        ms_map.extent.minx = extent.xMinimum()
        ms_map.extent.miny = extent.yMinimum()
        ms_map.extent.maxx = extent.xMaximum()
        ms_map.extent.maxy = extent.yMaximum()
        ms_map.setProjection( _toUtf8( self.canvas.mapRenderer().destinationCrs().toProj4() ) )

        if self.txtMapShapePath.text() != "":
            ms_map.shapepath = _toUtf8( self.getMapShapePath() )

        # image section
        r,g,b,a = self.canvas.canvasColor().getRgb()
        ms_map.imagecolor.setRGB( r, g, b )    #255,255,255
        ms_map.setImageType( _toUtf8( self.cmbMapImageType.currentText() ) )
        ms_outformat = ms_map.getOutputFormatByName( ms_map.imagetype )
        ms_outformat.transparent = self.onOffMap[ True ]

        # legend section
        #r,g,b,a = self.canvas.canvasColor().getRgb()
        #ms_map.legend.imageColor.setRgb( r, g, b )
        #ms_map.legend.status = mapscript.MS_ON
        #ms_map.legend.keysizex = 18
        #ms_map.legend.keysizey = 12
        #ms_map.legend.label.type = mapscript.MS_BITMAP
        #ms_map.legend.label.size = MEDIUM??
        #ms_map.legend.label.color.setRgb( 0, 0, 89 )
        #ms_map.legend.label.partials = self.trueFalseMap[ self.checkBoxPartials ]
        #ms_map.legend.label.force = self.trueFalseMap[ self.checkBoxForce ]
        #ms_map.legend.template = "[templatepath]"

        # web section
        ms_map.web.imagepath = _toUtf8( self.getWebImagePath() )
        ms_map.web.imageurl = _toUtf8( self.getWebImageUrl() )
        ms_map.web.temppath = _toUtf8( self.getWebTemporaryPath() )

        # web template
        ms_map.web.template = _toUtf8( self.getTemplatePath() )
        ms_map.web.header = _toUtf8( self.getTemplateHeaderPath() )
        ms_map.web.footer = _toUtf8( self.getTemplateFooterPath() )

        # map metadata
        ms_map.setMetaData( "ows_title", ms_map.name )
        ms_map.setMetaData( "ows_onlineresource", _toUtf8( u"%s?map=%s" % (self.txtMapServerUrl.text(), self.txtMapFilePath.text()) ) )
        srsList = []
        srsList.append( _toUtf8( self.canvas.mapRenderer().destinationCrs().authid() ) )
        ms_map.setMetaData( "ows_srs", ' '.join(srsList) )
        ms_map.setMetaData( "ows_enable_request", "*" )

        for layer in self.legend.layers():
            # check if layer is a supported type... seems return None if type is not supported (e.g. csv)
            if ( self.getLayerType( layer ) == None):
                QMessageBox.warning(self, "RT MapServer Exporter", "Skipped not supported layer: %s" % layer.name())
                continue
            
            # create a layer object
            ms_layer = mapscript.layerObj( ms_map )
            ms_layer.name = _toUtf8( layer.name() )
            ms_layer.type = self.getLayerType( layer )
            ms_layer.status = self.onOffMap[ self.legend.isLayerVisible( layer ) ]

            # layer extent
            extent = layer.extent()
            ms_layer.extent.minx = extent.xMinimum()
            ms_layer.extent.miny = extent.yMinimum()
            ms_layer.extent.maxx = extent.xMaximum()
            ms_layer.extent.maxy = extent.yMaximum()

            ms_layer.setProjection( _toUtf8( layer.crs().toProj4() ) )

            if layer.hasScaleBasedVisibility():
                ms_layer.minscaledenom = layer.minimumScale()
                ms_layer.maxscaledenom = layer.maximumScale()

            ms_layer.setMetaData( "ows_title", ms_layer.name )

            # layer connection
            if layer.providerType() == 'postgres':
                ms_layer.setConnectionType( mapscript.MS_POSTGIS, "" )
                uri = QgsDataSourceURI( layer.source() )
                ms_layer.connection = _toUtf8( uri.connectionInfo() )
                data = u"%s FROM %s" % ( uri.geometryColumn(), uri.quotedTablename() )
                if uri.keyColumn() != "":
                    data += u" USING UNIQUE %s" % uri.keyColumn()
                data += u" USING UNIQUE %s" % layer.crs().postgisSrid()
                if uri.sql() != "":
                  data += " FILTER (%s)" % uri.sql()
                ms_layer.data = _toUtf8( data )

            elif layer.providerType() == 'wms':
                ms_layer.setConnectionType( mapscript.MS_WMS, "" )

                uri = QUrl( "http://www.fake.eu/?"+layer.source() )
                ms_layer.connection = _toUtf8( uri.queryItemValue("url") )

                # loop thru wms sub layers
                wmsNames = []
                wmsStyles = []
                wmsLayerNames = layer.dataProvider().subLayers()
                wmsLayerStyles = layer.dataProvider().subLayerStyles()
                
                for index in range(len(wmsLayerNames)):
                    wmsNames.append( _toUtf8( wmsLayerNames[index] ) )
                    wmsStyles.append( _toUtf8( wmsLayerStyles[index] ) )

                # output SRSs
                srsList = []
                srsList.append( _toUtf8( layer.crs().authid() ) )

                # Create necessary wms metadata
                ms_layer.setMetaData( "ows_name", ','.join(wmsNames) )
                ms_layer.setMetaData( "wms_server_version", "1.1.1" )
                ms_layer.setMetaData( "ows_srs", ' '.join(srsList) )
                #ms_layer.setMetaData( "wms_format", layer.format() )
                ms_layer.setMetaData( "wms_format", ','.join(wmsStyles) )

            elif layer.providerType() == 'wfs':
                ms_layer.setConnectionType( mapscript.MS_WMS, "" )
                uri = QgsDataSourceURI( layer.source() )
                ms_layer.connection = _toUtf8( uri.uri() )

                # output SRSs
                srsList = []
                srsList.append( _toUtf8( layer.crs().authid() ) )

                # Create necessary wms metadata
                ms_layer.setMetaData( "ows_name", ms_layer.name )
                #ms_layer.setMetaData( "wfs_server_version", "1.1.1" )
                ms_layer.setMetaData( "ows_srs", ' '.join(srsList) )

            elif layer.providerType() == 'spatialite':
                ms_layer.setConnectionType( mapscript.MS_OGR, "" )
                uri = QgsDataSourceURI( layer.source() )
                ms_layer.connection = _toUtf8( uri.database() )
                ms_layer.data = _toUtf8( uri.table() )

            elif layer.providerType() == 'ogr':
                #ms_layer.setConnectionType( mapscript.MS_OGR, "" )
                ms_layer.data = _toUtf8( layer.source().split('|')[0] )

            else:
                ms_layer.data = _toUtf8( layer.source() )

            # set layer style
            if layer.type() == QgsMapLayer.RasterLayer:
                if hasattr(layer, 'renderer'):    # QGis >= 1.9
                    # layer.renderer().opacity() has range [0,1]
                    # ms_layer.opacity has range [0,100] => scale!
                    opacity = int( round(100 * layer.renderer().opacity()) )
                else:
                    opacity = int( 100 * layer.getTransparency() / 255.0 )
                ms_layer.opacity = opacity

            else:
                # use a SLD file set the layer style
                tempSldFile = QTemporaryFile("rt_mapserver_exporter-XXXXXX.sld")
                tempSldFile.open()
                tempSldPath = tempSldFile.fileName()
                tempSldFile.close()
                
                # export the QGIS layer style to SLD file
                errMsg, ok = layer.saveSldStyle( tempSldPath )
                if not ok:
                    QgsMessageLog.logMessage( errMsg, "RT MapServer Exporter" )
                else:
                    # set the mapserver layer style from the SLD file
                    #QFile.copy(tempSldPath, tempSldPath+".save")
                    #print "SLD saved file: ", tempSldPath+".save"
                    with open( unicode(tempSldPath), 'r' ) as fin:
                        sldContents = fin.read()
                    if mapscript.MS_SUCCESS != ms_layer.applySLD( sldContents, ms_layer.name ):
                        QgsMessageLog.logMessage( u"Something went wrong applying the SLD style to the layer '%s'" % ms_layer.name, "RT MapServer Exporter" )
                    QFile.remove( tempSldPath )

                    # set layer labels
                    #XXX the following code MUST be removed when QGIS will
                    # have SLD label support
                    labelingEngine = self.canvas.mapRenderer().labelingEngine()
                    if labelingEngine and labelingEngine.willUseLayer( layer ):
                        palLayer = labelingEngine.layer( layer.id() )
                        if palLayer.enabled:
                            if not palLayer.isExpression:
                                ms_layer.labelitem = _toUtf8( palLayer.fieldName )
                            else:
                                #XXX expressions won't be supported until
                                # QGIS have SLD label support
                                pass
        
                            if palLayer.scaleMin > 0:
                                ms_layer.labelminscaledenom = palLayer.scaleMin
                            if palLayer.scaleMax > 0:
                                ms_layer.labelmaxscaledenom = palLayer.scaleMax
        
                            ms_label = mapscript.labelObj()
        
                            ms_label.type = mapscript.MS_TRUETYPE
                            ms_label.antialias = mapscript.MS_TRUE
        
                            ms_label.position = self.getLabelPosition( palLayer )
                            # TODO: convert offset to pixels
                            ms_label.offsetx = int( palLayer.xOffset )
                            ms_label.offsety = int( palLayer.yOffset )
                            ms_label.angle = palLayer.angleOffset
        
                            # set label font name, size and color
                            fontFamily = palLayer.textFont.family().replace(" ", "")
                            fontStyle = palLayer.textNamedStyle.replace(" ", "")
                            ms_label.font = _toUtf8( u"%s-%s" % (fontFamily, fontStyle) )
                            if palLayer.textFont.pixelSize() > 0:
                                ms_label.size = int( palLayer.textFont.pixelSize() )
                            r,g,b,a = palLayer.textColor.getRgb()
                            ms_label.color.setRGB( r, g, b )
        
                            if palLayer.fontLimitPixelSize:
                                ms_label.minsize = palLayer.fontMinPixelSize
                                ms_label.maxsize = palLayer.fontMaxPixelSize
                            ms_label.wrap = _toUtf8( palLayer.wrapChar )
        
                            ms_label.priority = palLayer.priority
        
                            # TODO: convert buffer size to pixels
                            ms_label.buffer = int( palLayer.bufferSize )
        
                            if int( palLayer.minFeatureSize ) > 0:
                                # TODO: convert feature size from mm to pixels
                                ms_label.minfeaturesize = int( palLayer.minFeatureSize )
        
                            ms_class = mapscript.classObj()
                            ms_class.addLabel( ms_label )
                            ms_layer.insertClass( ms_class )


        # save the map file now!
        if mapscript.MS_SUCCESS != ms_map.save( _toUtf8( self.txtMapFilePath.text() )     ):
            return

        # Most of the following code does not use mapscript because it asserts
        # paths you supply exists, but this requirement is usually not meet on
        # the QGIS client used to generate the mafile.

        # get the mapfile content as string so we can manipulate on it
        mesg = "Reload Map file %s to manipulate it" % self.txtMapFilePath.text()
        QgsMessageLog.logMessage( mesg, "RT MapServer Exporter" )
        fin = open( _toUtf8(self.txtMapFilePath.text()), 'r' )
        parts = []
        line = fin.readline()
        while line != "":
            line = line.rstrip('\n')
            parts.append(line)
            line = fin.readline()
        fin.close()
        
        partsContentChanged = False

        # retrieve the list of used font aliases searching for FONT keywords
        fonts = []
        searchFontRx = re.compile("^\\s*FONT\\s+")
        for line in filter(searchFontRx.search, parts):
            # get the font alias, remove quotes around it
            fontName = re.sub(searchFontRx, "", line)[1:-1]
            # remove spaces within the font name
            fontAlias = fontName.replace(" ", "")

            # append the font alias to the font list
            if fontAlias not in fonts:
                fonts.append( fontAlias )

                # update the font alias in the mapfile
                # XXX: the following lines cannot be removed since the SLD file
                # could refer a font whose name contains spaces. When SLD specs
                # ate clear on how to handle fonts than we'll think whether
                # remove it or not.
                replaceFontRx = re.compile( u"^(\\s*FONT\\s+\")%s(\".*)$" % QRegExp.escape(fontName) )
                parts = [ replaceFontRx.sub(u"\g<1>%s\g<2>" % fontAlias, part) for part in parts ]
                partsContentChanged = True

        # create the file containing the list of font aliases used in the
        # mapfile
        if self.checkCreateFontFile.isChecked():
            fontPath = QFileInfo(_toUtf8(self.txtMapFilePath.text())).dir().filePath(u"fonts.txt")
            with open( unicode(fontPath), 'w' ) as fout:
                for fontAlias in fonts:
                    fout.write( unicode(fontAlias) )

        # add the FONTSET keyword with the associated path
        if self.txtMapFontsetPath.text() != "":
            # get the index of the first instance of MAP string in the list
            pos = parts.index( filter(lambda x: re.compile("^MAP(\r\n|\r|\n)*$").match(x), parts)[0] )
            if pos >= 0:
                parts.insert( pos+1, u'  FONTSET "%s"' % self.txtMapFontsetPath.text() )
                partsContentChanged = True
            else:
                QgsMessageLog.logMessage( u"'FONTSET' keyword not added to the mapfile: unable to locate the 'MAP' keyword...", "RT MapServer Exporter" )

        # if mapfile content changed, store the file again at the same path
        if partsContentChanged:
            with open( _toUtf8(self.txtMapFilePath.text()), 'w' ) as fout:
                for part in parts:
                    fout.write( part+"\n" )

        # XXX for debugging only: let's have a look at the map result! :)
        # XXX it works whether the file pointed by the fontset contains ALL the
        # aliases of fonts referred from the mapfile.
        #ms_map = mapscript.mapObj( unicode( self.txtMapFilePath.text() ) )
        #ms_map.draw().save( _toUtf8( self.txtMapFilePath.text() + ".png" )    , ms_map )

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
            layer = QgsMapLayerRegistry.instance().mapLayer( lid )
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
            with open( unicode(tmplPath), 'w' ) as fout:
                fout.write( tmplContent )
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

