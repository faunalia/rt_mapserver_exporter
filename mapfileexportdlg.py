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

from mapfileexportdlg_ui import Ui_MapfileExportDlg
import mapscript

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
        if palLabel.yQuadOffset == 1:
            if palLabel.xQuadOffset == -1:
                return mapscript.MS_UL
            elif palLabel.xQuadOffset == 0:
                return mapscript.MS_UC
            elif palLabel.xQuadOffset == 1:
                return mapscript.MS_UR
        elif palLabel.yQuadOffset == 0:
            if palLabel.xQuadOffset == -1:
                return mapscript.MS_CL
            elif palLabel.xQuadOffset == 0:
                return mapscript.MS_CC
            elif palLabel.xQuadOffset == 1:
                return mapscript.MS_CR
        elif palLabel.yQuadOffset == -1:
            if palLabel.xQuadOffset == -1:
                return mapscript.MS_LL
            elif palLabel.xQuadOffset == 0:
                return mapscript.MS_LC
            elif palLabel.xQuadOffset == 1:
                return mapscript.MS_LR
        return mapscript.MS_AUTO


    def __init__(self, iface, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.legend = self.iface.legendInterface()

        # get the default title from the project
        title = QgsProject.instance().title()
        if title == "":
            title = QFileInfo( QgsProject.instance().fileName() ).completeBaseName()
        if title != "":
            self.txtMapName.setText( title )

        # fill the image format combo
        self.cmbMapImageType.addItems( QStringList(["png", "gif", "jpeg", "svg", "GTiff"]) )

        QObject.connect( self.btnChooseFile, SIGNAL("clicked()"), self.selectMapFile )

    def selectMapFile(self):
        # retrieve the last used map file path
        settings = QSettings()
        lastUsedFile = settings.value("/RT MapServer Exporter/lastUsedFile", "").toString()

        # ask for choosing where to store the map file
        filename = QFileDialog.getSaveFileName(self, "Select where to save the map file", lastUsedFile, "MapFile (*.map)")
        if filename == "":
            return

        # store the last used map file path
        settings.setValue("/RT MapServer Exporter/lastUsedFile", filename)
        # update the displayd path
        self.txtMapFilePath.setText( filename )

    def accept(self):
        # create a new ms_map
        ms_map = mapscript.mapObj()
        ms_map.name = unicode( self.txtMapName.text() ).encode('utf8')

        # map size
        (width, widthOk), (height, heightOk) = self.txtMapWidth.text().toInt(), self.txtMapHeight.text().toInt()
        if widthOk and heightOk:
            ms_map.setSize( width, height )

        # map units
        ms_map.units = self.unitMap[ self.canvas.mapUnits() ]
        if self.cmbMapUnits.currentIndex() >= 0:
            units, ok = self.cmbMapUnits.itemData( self.cmbMapUnits.currentIndex() ).toInt()
            if ok:
                ms_map.units = units

        # map extent
        extent = self.canvas.fullExtent()
        ms_map.extent.minx = extent.xMinimum()
        ms_map.extent.miny = extent.yMinimum()
        ms_map.extent.maxx = extent.xMaximum()
        ms_map.extent.maxy = extent.yMaximum()
        ms_map.setProjection( unicode( self.canvas.mapRenderer().destinationCrs().toProj4() ).encode('utf8') )

        if self.txtMapShapePath.text() != "":
            ms_map.shapepath = unicode( self.txtMapShapePath.text() ).encode('utf8')

        # image section
        r,g,b,a = self.canvas.canvasColor().getRgb()
        ms_map.imagecolor.setRGB( r, g, b )    #255,255,255
        ms_map.imagequality = 95
        ms_map.setImageType( unicode( self.cmbMapImageType.currentText() ).encode('utf8') )

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

        # web section
        ms_map.web.imagepath = "/tmp/"
        ms_map.web.imageurl = "/tmp/"

        # map metadata
        ms_map.setMetaData( "ows_title", ms_map.name )
        ms_map.setMetaData( "ows_onlineresource", unicode( u"%s?map=%s" % (self.txtMapServerUrl.text(), self.txtMapFilePath.text()) ).encode('utf8') )
        srsList = []
        srsList.append( unicode( self.canvas.mapRenderer().destinationCrs().authid() ).encode('utf8') )
        ms_map.setMetaData( "ows_srs", ' '.join(srsList) )
        ms_map.setMetaData( "ows_enable_request", "*" )

        for layer in self.legend.layers():
            # create a layer object
            ms_layer = mapscript.layerObj( ms_map )
            ms_layer.name = unicode( layer.name() ).encode('utf8')
            ms_layer.type = self.getLayerType( layer )
            ms_layer.status = self.onOffMap[ self.legend.isLayerVisible( layer ) ]

            # layer extent
            extent = layer.extent()
            ms_layer.extent.minx = extent.xMinimum()
            ms_layer.extent.miny = extent.yMinimum()
            ms_layer.extent.maxx = extent.xMaximum()
            ms_layer.extent.maxy = extent.yMaximum()

            ms_layer.setProjection( unicode( layer.crs().toProj4() ).encode('utf8') )

            if layer.hasScaleBasedVisibility():
                ms_layer.minscaledenom = layer.minimumScale()
                ms_layer.maxscaledenom = layer.maximumScale()

            ms_layer.setMetaData( "ows_title", ms_layer.name )

            # layer connection
            if layer.providerType() == 'postgres':
                ms_layer.setConnectionType( mapscript.MS_POSTGIS, "" )
                uri = QgsDataSourceURI( layer.source() )
                ms_layer.connection = unicode( uri.connectionInfo() ).encode('utf8')
                data = u"%s FROM %s" % ( uri.geometryColumn(), uri.quotedTablename() )
                if uri.keyColumn() != "":
                    data += u" USING UNIQUE %s" % uri.keyColumn()
                data += u" USING UNIQUE %s" % layer.crs().postgisSrid()
                if uri.sql() != "":
                  data += " FILTER (%s)" % uri.sql()
                ms_layer.data = unicode( data ).encode('utf8')

            elif layer.providerType() == 'wms':
                ms_layer.setConnectionType( mapscript.MS_WMS, "" )
                uri = QgsDataSourceURI( layer.source() )
                ms_layer.connection = unicode( uri.paramValue("url") ).encode('utf8')

                # loop thru wms sub layers
                names = []
                styles = []
                wmsLayerNames = uri.paramValues("layers")
                wmsLayerStyles = uri.paramValues("styles")
                for index in range(len(wmsLayerNames)): 
                    wmsNames.append( unicode( wmsLayerNames[index] ).encode('utf8') )
                    wmsStyles.append( unicode( wmsLayerStyles[index] ).encode('utf8') )

                # output SRSs
                srsList = []
                srsList.append( unicode( layer.crs().authid() ).encode('utf8') )

                # Create necessary wms metadata
                ms_layer.setMetaData( "ows_name", ','.join(wmsNames) )
                ms_layer.setMetaData( "wms_server_version", "1.1.1" )
                ms_layer.setMetaData( "ows_srs", ' '.join(srsList) )
                #ms_layer.setMetaData( "wms_format", layer.format() )
                ms_layer.setMetaData( "wms_format", ','.join(wmsStyles) )

            elif layer.providerType() == 'wfs':
                ms_layer.setConnectionType( mapscript.MS_WMS, "" )
                uri = QgsDataSourceURI( layer.source() )
                ms_layer.connection = unicode( uri.uri() ).encode('utf8')

                # output SRSs
                srsList = []
                srsList.append( unicode( layer.crs().authid() ).encode('utf8') )

                # Create necessary wms metadata
                ms_layer.setMetaData( "ows_name", ms_layer.name )
                #ms_layer.setMetaData( "wfs_server_version", "1.1.1" )
                ms_layer.setMetaData( "ows_srs", ' '.join(srsList) )

            elif layer.providerType() == 'ogr':
                ms_layer.data = unicode( layer.source().split('|')[0] ).encode('utf8')

            else:
                ms_layer.data = unicode( layer.source() ).encode('utf8')

            # set layer style
            if layer.type() == QgsMapLayer.RasterLayer:
                if hasattr(layer, 'renderer'):    # QGis >= 1.9
                    opacity = layer.renderer().opacity()
                else:
                    opacity = int( 100 * layer.getTransparency() / 255.0 )
                ms_layer.opacity = opacity

            else:
                # use a SLD file set the layer style
                tempSldFile = QTemporaryFile("RT MapServer Exporter-XXXXXX.sld")
                tempSldFile.open()
                tempSldPath = tempSldFile.fileName()
                tempSldFile.close()

                # export the QGIS layer style to SLD file
                errMsg, ok = layer.saveSldStyle( tempSldPath )
                if not ok:
                    QgsMessageLog.logMessage( errMsg, "RT MapServer Exporter" )
                else:
                    # set the mapserver layer style from the SLD file
                    with open( unicode(tempSldPath), 'r' ) as fin:
                        sldContents = fin.read()
                    if mapscript.MS_SUCCESS != ms_layer.applySLD( sldContents, ms_layer.name ):
                        QgsMessageLog.logMessage( u"An error occurs applying the SLD style", "RT MapServer Exporter" )
                    QFile.remove( tempSldPath )

            # set layer labels
            labelingEngine = self.canvas.mapRenderer().labelingEngine()
            if labelingEngine and labelingEngine.willUseLayer( layer ):
                palLayer = labelingEngine.layer( layer.id() )
                if palLayer.enabled:
                    if not palLayer.isExpression:
                        ms_layer.labelitem = unicode( palLayer.fieldName ).encode('utf8')
                    else:
                        # TODO: expressions are not supported yet
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

                    r,g,b,a = palLayer.textColor.getRgb()
                    ms_label.color.setRGB( r, g, b )
                    ms_label.font = unicode( palLayer.textFont.family() ).encode('utf8')
                    if palLayer.textFont.pixelSize() > 0:
                        ms_label.size = int( palLayer.textFont.pixelSize() )
                    if palLayer.fontLimitPixelSize:
                        ms_label.minsize = palLayer.fontMinPixelSize
                        ms_label.maxsize = palLayer.fontMaxPixelSize
                    ms_label.wrap = unicode( palLayer.wrapChar ).encode('utf8')

                    # TODO: convert buffer size to pixels
                    ms_label.buffer = int( palLayer.bufferSize )
                    # TODO: convert feature size from mm to pixels
                    ms_label.minfeaturesize = int( palLayer.minFeatureSize )

                    ms_class = mapscript.classObj()
                    ms_class.addLabel( ms_label )
                    ms_layer.insertClass( ms_class )
        

        # save the map file now!
        if mapscript.MS_SUCCESS != ms_map.save( unicode( self.txtMapFilePath.text() ).encode('utf8') ):
            return

        # get the mapfile content so we can work on it
        with open( unicode(self.txtMapFilePath.text()), 'r' ) as fin:
            partsContentChanged = False
            parts = QString(fin.read()).split(u"\n")

        if self.checkCreateFontFile.isChecked():
            # get the list of used fonts, search for FONT keywords
            fonts = []
            searchFontRx = QRegExp("^\\s*FONT\\s+")
            for line in parts.filter( searchFontRx ):
                # remove the quotes
                fontName = line.replace(searchFontRx, "")[1:-1]
                if fonts.count( fontName ) == 0:
                    fonts.append( fontName )

            letterNumRx = QRegExp("[^-a-zA-Z0-9_]")
            for index, fontName in enumerate(fonts):
                fontRx = QRegExp( "^(\\s*FONT\\s+)([\"'])%s(\\2\\s*)$" % QRegExp.escape(fontName) )
                fontAlias = QString(fontName).replace(letterNumRx, "-")
                parts = parts.replaceInStrings( fontRx, "\\1\\2%s\\3" % fontAlias )
                partsContentChanged = True

                # update fonts list
                fonts[index] = fontAlias

            # create the font file
            fontPath = QFileInfo(self.txtMapFilePath.text()).dir().filePath(u"fonts.txt")
            with open( unicode(fontPath), 'w' ) as fout:
                letterNumRx = QRegExp("[^-a-zA-Z0-9_]")
                for fontName in fonts:
                    fontFile = fontName.toLower() # "/usr/share/fonts/truetype/ubuntu-font-family/Ubuntu-C"
                    fout.write( u"%s\t\t%s.ttf" % (fontName, fontFile) )

            # XXX for debugging only
            self.txtMapFontsetPath.setText( fontPath )

        if self.txtMapFontsetPath.text() != "":
            # add the FONTSET keyword with the associated path
            pos = parts.indexOf( QRegExp("^MAP$") )
            if pos >= 0:
                parts.insert( pos+1, u'  FONTSET "%s"' % self.txtMapFontsetPath.text() )
                partsContentChanged = True
            else:
                QgsMessageLog.logMessage( u"Unable to locate the 'WEB' keyword in the map file...", "RT MapServer Exporter" )

        if partsContentChanged:
            # store the file again at the same position
            with open( unicode(self.txtMapFilePath.text()), 'w' ) as fout:
                fout.write( unicode( parts.join(u"\n") ) )

        # let's have a look at the map result! :)
        ms_map = mapscript.mapObj( unicode( self.txtMapFilePath.text() ) )
        ms_map.draw().save( unicode( self.txtMapFilePath.text() + ".png" ).encode('utf8'), ms_map )

        QDialog.accept(self)

