import re

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from utils import *
from utils import toUTF8

import Serialization

DEFAULT_WIDTH = 600
DEFAULT_HEIGHT= 600

def export(
    name = u'',
    width = DEFAULT_WIDTH,
    height = DEFAULT_HEIGHT,
    units = mapscript.MS_METERS,
    extent = QgsRectangle(),
    projection = str(QgsCoordinateReferenceSystem('4326').toProj4()),
    shapePath = u'',
    backgroundColor = QColor(),
    imageType = u'PNG',
    imagePath = u'',
    imageURL = u'',
    tempPath = u'',
    validationRegexp = u'',
    templatePath = u'',
    templateHeaderPath = u'',
    templateFooterPath = u'',
    mapServerURL = u'',
    mapfilePath = u'',
    createFontFile = True,
    fontsetPath = u'',
    layers = [],
    legend = None,
    canvas = QgsMapCanvas()
):
    QgsMessageLog.logMessage(mapfilePath, 'MapServer exporter')

    # Create a new msMap
    msMap = mapscript.mapObj()
    msMap.name = name

    # map size
    widthOk, heightOk = isinstance(width, int), isinstance(height, int)
    if widthOk and heightOk:
        msMap.setSize(width, height)

    # map units
    msMap.units = units

    # map extent
    msMap.extent.minx = extent.xMinimum()
    msMap.extent.miny = extent.yMinimum()
    msMap.extent.maxx = extent.xMaximum()
    msMap.extent.maxy = extent.yMaximum()
    msMap.setProjection(projection)

    if shapePath != "":
        msMap.shapepath = shapePath

    # image section
    msMap.imagecolor.setRGB(backgroundColor.red(), backgroundColor.green(), backgroundColor.blue())
    msMap.setImageType(imageType)
    msOutformat = msMap.getOutputFormatByName(msMap.imagetype)
    msOutformat.transparent = onOffMap[False]

    # web section
    msMap.web.imagepath = imagePath
    msMap.web.imageurl = imageURL
    msMap.web.temppath = tempPath
    
    # add validation block if set a regexp
    # no control on regexp => it will be done by mapscript applySld
    # generating error in case regexp is wrong
    if validationRegexp != '':
        msMap.web.validation.set('sld_external_graphic', validationRegexp)

    # Web template
    msMap.web.template = templatePath
    msMap.web.header = templateHeaderPath
    msMap.web.footer = templateFooterPath

    # Map metadata
    msMap.setMetaData('ows_title', msMap.name)
    msMap.setMetaData('ows_onlineresource', toUTF8(u'%s?map=%s' % (mapServerURL, mapfilePath)))
    srsList = []
    srsList.append(toUTF8(canvas.mapRenderer().destinationCrs().authid()))
    msMap.setMetaData('ows_srs', ' '.join(srsList))
    msMap.setMetaData('ows_enable_request', '*')

    # Iterate through layers
    for layer in layers:

        # Check if layer is a supported type... seems return None if type is not supported (e.g. csv)
        if (utils.getLayerType(layer) == None):
            QMessageBox.warning(
                self, 
                'RT MapServer Exporter',
                'Skipped not supported layer: %s' % layer.name()
            )
            continue
        
        # Create a layer object
        msLayer = mapscript.layerObj(msMap)
        msLayer.name = toUTF8(layer.name())
        msLayer.type = utils.getLayerType(layer)
        msLayer.status =  utils.onOffMap[legend.isLayerVisible(layer)]

        # Layer extent and scale-based visibility
        extent = layer.extent()
        msLayer.extent.minx = extent.xMinimum()
        msLayer.extent.miny = extent.yMinimum()
        msLayer.extent.maxx = extent.xMaximum()
        msLayer.extent.maxy = extent.yMaximum()

        if layer.hasScaleBasedVisibility():
            msLayer.minscaledenom = layer.minimumScale()
            msLayer.maxscaledenom = layer.maximumScale()

        # Layer projection
        msLayer.setProjection(toUTF8(layer.crs().toProj4()))


        msLayer.setMetaData('ows_title', msLayer.name)
        msLayer.setMetaData('ows_srs', str(layer.crs().authid()))
        msLayer.setMetaData('gml_include_items', 'all')

        # Layer connection
        if layer.providerType() == 'postgres':
            msLayer.setConnectionType(mapscript.MS_POSTGIS, '')

            uri = QgsDataSourceURI(layer.source())
            msLayer.connection = toUTF8(uri.connectionInfo())

            data = u'%s FROM %s' % (uri.geometryColumn(), uri.quotedTablename())

            if uri.keyColumn() != '':
                data += u' USING UNIQUE %s' % uri.keyColumn()

            data += u' USING UNIQUE %s' % layer.crs().postgisSrid()

            if uri.sql() != '':
                data += u' FILTER (%s)' % uri.sql()

            msLayer.data = toUTF8(data)

        elif layer.providerType() == 'wms':
            msLayer.setConnectionType(mapscript.MS_WMS, '')
            uri = QUrl('http://www.fake.eu/?' + layer.source())
            msLayer.connection = toUTF8(uri.queryItemValue('url'))

            # loop thru wms sub layers
            wmsNames = []
            wmsStyles = []
            wmsLayerNames = layer.dataProvider().subLayers()
            wmsLayerStyles = layer.dataProvider().subLayerStyles()
            
            for index in range(len(wmsLayerNames)):
                wmsNames.append(toUTF8(wmsLayerNames[index]))
                wmsStyles.append(toUTF8(wmsLayerStyles[index]))

            # output SRSs
            srsList = []
            srsList.append(toUTF8(layer.crs().authid()))

            # Create necessary wms metadata
            msLayer.setMetaData('ows_name', ','.join(wmsNames))
            msLayer.setMetaData('wmsServer_version', '1.1.1')
            msLayer.setMetaData('ows_srs', ' '.join(srsList))
            msLayer.setMetaData('wmsFormat', ','.join(wmsStyles))

        elif layer.providerType() == 'wfs':
            msLayer.setConnectionType(mapscript.MS_WMS, '')
            uri = QgsDataSourceURI(layer.source())
            msLayer.connection = toUTF8(uri.uri())

            # Output SRSs
            srsList = []
            srsList.append(toUTF8(layer.crs().authid()))

            # Create necessary wms metadata
            msLayer.setMetaData('ows_name', msLayer.name)
            msLayer.setMetaData('ows_srs', ' '.join(srsList))

        elif layer.providerType() == 'spatialite':
            msLayer.setConnectionType(mapscript.MS_OGR, '')
            uri = QgsDataSourceURI(layer.source())
            msLayer.connection = toUTF8(uri.database())
            msLayer.data = toUTF8(uri.table())

        elif layer.providerType() == 'ogr':
            msLayer.data = toUTF8(layer.source().split('|')[0])

        else:
            msLayer.data = toUTF8(layer.source())

        # Set layer style
        if layer.type() == QgsMapLayer.RasterLayer:
            if hasattr(layer, 'renderer'):    # QGis >= 1.9
                # layer.renderer().opacity() has range [0,1]
                # msLayer.opacity has range [0,100] => scale!
                opacity = int(round(100 * layer.renderer().opacity()))
            else:
                opacity = int(100 * layer.getTransparency() / 255.0)
            msLayer.opacity = opacity

        else:
            # This is a supported vector layer.
            #
            # In this case we use our custom style serializers (see: Serialization.py) here as the
            # differences between the SLD implementation in MapServer and QGis makes it impossible
            # to transfer complex styles using SLD.
            #
            # Please note that we only emit font definitions in the label style serializer
            # if a fontset path is supplied. Otherwise we fall back to the default font.
            # (Font size is set under all circumstances, though.) 
            #
            Serialization.VectorLayerStyleSerializer(layer, msLayer, msMap)
            Serialization.LabelStyleSerializer(layer, msLayer, msMap, fontsetPath != '')

    # Save the map file
    if mapscript.MS_SUCCESS != msMap.save(mapfilePath):
        return

    # Most of the following code does not use mapscript because it asserts
    # paths you supply exists, but this requirement is usually not met on
    # the QGIS client used to generate the mapfile.

    # Get the mapfile content as string so we can manipulate on it
    mesg = 'Reload Map file %s to manipulate it' % mapfilePath
    QgsMessageLog.logMessage(mesg, 'RT MapServer Exporter')
    fin = open(mapfilePath, 'r')
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
        fontName = re.sub(searchFontRx, '', line)[1:-1]
        # remove spaces within the font name
        fontAlias = fontName.replace(' ', '')

        # append the font alias to the font list
        if fontAlias not in fonts:
            fonts.append(fontAlias)

            # update the font alias in the mapfile
            # XXX: the following lines cannot be removed since the SLD file
            # could refer a font whose name contains spaces. When SLD specs
            # ate clear on how to handle fonts than we'll think whether
            # remove it or not.
            replaceFontRx = re.compile(u"^(\\s*FONT\\s+\")%s(\".*)$" % QRegExp.escape(fontName))
            parts = [ replaceFontRx.sub(u"\g<1>%s\g<2>" % fontAlias, part) for part in parts ]
            partsContentChanged = True

    # create the file containing the list of font aliases used in the
    # mapfile
    if createFontFile: 
        fontPath = QFileInfo(mapfilePath).dir().filePath(u'fonts.txt')
        with open(unicode(fontPath), 'w') as fout:
            for fontAlias in fonts:
                fout.write(unicode(fontAlias))

    # add the FONTSET keyword with the associated path
    if fontsetPath != '':
        # get the index of the first instance of MAP string in the list
        pos = parts.index(filter(lambda x: re.compile("^MAP(\r\n|\r|\n)*$").match(x), parts)[0])
        if pos >= 0:
            parts.insert(pos + 1, u'  FONTSET "%s"' % fontsetPath)
            partsContentChanged = True
        else:
            QgsMessageLog.logMessage(
                u'"FONTSET" keyword not added to the mapfile: unable to locate the "MAP" keyword...',
                u'RT MapServer Exporter'
            )

    # if mapfile content changed, store the file again at the same path
    if partsContentChanged:
        with open(mapfilePath, 'w') as fout:
            for part in parts:
                fout.write(part + "\n")
