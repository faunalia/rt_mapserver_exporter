import mapscript

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

import SerializationUtils as utils

class SLDSerializer(object):
    def __init__(self, layer, msLayer, msMap):

        # Create a temporary .SLD file
        tempSldFile = QTemporaryFile("rt_mapserver_exporter-XXXXXX.sld")
        tempSldFile.open()
        tempSldPath = tempSldFile.fileName()
        tempSldFile.close()
        
        # Export the QGIS layer style to the .SLD file
        errMsg, ok = layer.saveSldStyle( tempSldPath )

        if not ok:
            QgsMessageLog.logMessage( errMsg, "RT MapServer Exporter" )
        else:
            #Set the mapserver layer style from the SLD file
            
            with open( unicode(tempSldPath), 'r' ) as fin:
                sldContents = fin.read()

            print msLayer.name;
            if mapscript.MS_SUCCESS != msLayer.applySLD( sldContents, msLayer.name ):
                QgsMessageLog.logMessage(
                    u"Something went wrong applying the SLD style to the layer '%s'" % msLayer.name,
                    "RT MapServer Exporter"
                )

            QFile.remove( tempSldPath )

class LabelStyleSerializer(object):
    def __init__(self, layer, msLayer, msMap, emitFontDefinitions=False):
        """Serialize labels of a QGis vector layer to mapscript"""

        self.layer = layer
        self.msLayer = msLayer
        self.msMap = msMap

        labelingEngine = QgsPalLabeling()
        labelingEngine.loadEngineSettings()

        if labelingEngine and labelingEngine.willUseLayer(self.layer):
            ps = QgsPalLayerSettings.fromLayer(self.layer)

            if not ps.isExpression:
                self.msLayer.labelitem = unicode(ps.fieldName).encode('utf-8')
            else:
                pass

            msLabel = mapscript.labelObj()

            msLabel.type = mapscript.MS_TRUETYPE
            msLabel.encoding = 'utf-8'
           
            # Position, rotation and scaling
            msLabel.position = utils.serializeLabelPosition(ps)
            msLabel.offsetx = int(ps.xOffset)
            msLabel.offsety = int(ps.yOffset)

            # Data defined rotation
            # Please note that this is the only currently supported data defined property.
            if QgsPalLayerSettings.Rotation in ps.dataDefinedProperties.keys():
                dd = ps.dataDefinedProperty(QgsPalLayerSettings.Rotation)
                rotField = unicode(dd.field()).encode('utf-8')
                msLabel.setBinding(mapscript.MS_LABEL_BINDING_ANGLE, rotField)
            else:
                msLabel.angle = ps.angleOffset

            if ps.scaleMin > 0:
                self.msLayer.labelminscaledenom = ps.scaleMin
            if ps.scaleMax > 0:
                self.msLayer.labelmaxscaledenom = ps.scaleMax

            fontDef, msLabel.size = utils.serializeFontDefinition(ps.textFont, ps.textNamedStyle)

            # `emitFontDefinitions` gets set based on whether a fontset path is supplied through 
            # the plugin UI. There is no point in emitting font definitions without a valid fontset,
            # so in that case we fall back to using whatever default font MapServer (thus the
            # underlying windowing system) provides.
            # Please note that substituting the default font only works in MapServer 7.0.0 and above.
            if emitFontDefinitions == True:
                msLabel.font = fontDef

            if ps.fontSizeInMapUnits:
                utils.maybeSetLayerSizeUnitFromMap(QgsSymbolV2.MapUnit, self.msLayer)

            # Font size and color
            msLabel.color = utils.serializeColor(ps.textColor)

            if ps.fontLimitPixelSize:
                msLabel.minsize = ps.fontMinPixelSize
                msLabel.maxsize = ps.fontMaxPixelSize

            # Other properties
            wrap = unicode(ps.wrapChar).encode('utf-8')
            if len(wrap) == 1:
                msLabel.wrap = wrap[0]
            elif len(wrap) > 1:
                QgsMessageLog.logMessage(
                    u'Skipping invalid wrap character ("%s") for labels.' % wrap.decode('utf-8'),
                    'RT MapServer Exporter'
                )
            else:
                # No wrap char set
                pass

            # Other properties
            msLabel.partials = labelingEngine.isShowingPartialsLabels()
            msLabel.force = ps.displayAll
            msLabel.priority = ps.priority
            msLabel.buffer = int(utils.sizeUnitToPx(
                ps.bufferSize,
                QgsSymbolV2.MapUnit if ps.bufferSizeInMapUnits else QgsSymbolV2.MM
            ))

            if ps.minFeatureSize > 0:
                msLabel.minfeaturesize = utils.sizeUnitToPx(ps.minFeatureSize)

            # Label definitions gets appended to the very first class on a layer, or to a new class
            # if no classes exist.
            msClass = msLayer.getClass(0) \
                if (msLayer.numclasses > 0) \
                else mapscript.classObj(msLayer)

            msClass.addLabel(msLabel)


            
class VectorLayerStyleSerializer(object):
    def __init__(self, rctx, layer, msLayer, msMap):
        """Serialize a QGis vector layer renderer into mapscript classes"""

        self.msLayer = msLayer
        self.msMap = msMap
        self.rctx = rctx

        # Set the size units to pixels here as that seems to be the most roboust
        # and independent of map units
        msLayer.sizeunits = mapscript.MS_PIXELS
    
        renderer = layer.rendererV2()

        # Dispatch based on renderer type
        if isinstance(renderer, QgsSingleSymbolRendererV2):
            self.serializeSingleSymbolRenderer(renderer)

        elif isinstance(renderer, QgsCategorizedSymbolRendererV2):
            self.serializeCategorizedSymbolRenderer(renderer)

        elif isinstance(renderer, QgsGraduatedSymbolRendererV2):
            self.serializeGraduatedSymbolRenderer(renderer)

        else:
            QgsMessageLog.logMessage(
                'Unhandled renderer type: %s' % type(renderer),
                'RT MapServer Exporter'
            )


    def serializeSingleSymbolRenderer(self, renderer):
        """Serialize a QGis single symbol renderer into a MapServer class"""

        msClass = mapscript.classObj(self.msLayer)

        for sym in renderer.symbols(self.rctx):
            SymbolLayerSerializer(sym, msClass, self.msLayer, self.msMap)


    def serializeCategorizedSymbolRenderer(self, renderer):
        """Serialize a QGis categorized symbol renderer into MapServer classes"""

        attr = renderer.usedAttributes()[0]
        i = 0

        for cat in renderer.categories():
            msClass = mapscript.classObj(self.msLayer)

            # XXX: type(cat.value()) differs whether the script is being run in QGis or as 
            # a standalone PyQGis application, so we convert it accordingly.
            cv = cat.value()
            cv = cv.toString() if isinstance(cv, QVariant) else unicode(cv)

            msClass.setExpression((u'("[%s]" = "%s")' % (attr, cv)).encode('utf-8'))
            SymbolLayerSerializer(renderer.symbols(self.rctx)[i], msClass, self.msLayer, self.msMap)
            #add number to class name
            msClass.name+='_'+str(i)
            i = i + 1


    def serializeGraduatedSymbolRenderer(self, renderer):
        """Serialize a QGis graduated symbol renderer into MapServer classes"""

        attr = unicode(renderer.usedAttributes()[0])
        i = 0

        for range in renderer.ranges():
            msClass = mapscript.classObj(self.msLayer)

            # We use '>=' instead of '>' when defining the first class to also include the lowest
            # value of the range in the expression.
            msClass.setExpression((u'(([%s] %s %f) And ([%s] <= %f))' % ( \
                attr, \
                '>=' if (i == 0) else '>', \
                range.lowerValue(), \
                attr, \
                range.upperValue() \
            )).encode('utf-8'))
            SymbolLayerSerializer(renderer.symbols(self.rctx)[i], msClass, self.msLayer, self.msMap)
            #add number to class name
            msClass.name+='_'+str(i)
            i = i + 1



class SymbolLayerSerializer(object):
    def __init__(self, sym, msClass, msLayer, msMap):
        """Serialize a QGis symbol layer into a MapServer style"""
        
        self.msClass = msClass
        self.msLayer = msLayer
        self.msMap = msMap
        msClass.name=msLayer.name
        for i in range(0, sym.symbolLayerCount()):
            sl = sym.symbolLayer(i)

            # Dispatch based on symbol layer type
            if isinstance(sl, QgsSimpleLineSymbolLayerV2):
                self.serializeSimpleLineSymbolLayer(sl)

            elif isinstance(sl, QgsSimpleFillSymbolLayerV2):
                self.serializeSimpleFillSymbolLayer(sl)

            elif isinstance(sl, QgsSimpleMarkerSymbolLayerV2):
                self.serializeSimpleMarkerSymbolLayer(sl)

            elif isinstance(sl, QgsFontMarkerSymbolLayerV2):
                self.serializeFontMarkerSymbolLayer(sl)

            elif isinstance(sl, QgsSvgMarkerSymbolLayerV2):
                self.serializeSvgMarkerSymbolLayer(sl)

            elif isinstance(sl, QgsPointPatternFillSymbolLayer):
                self.serializePointPatternFillSymbolLayer(sl)

            elif isinstance(sl, QgsLinePatternFillSymbolLayer):
                self.serializeLinePatternFillSymbolLayer(sl)

            else:
                QgsMessageLog.logMessage(
                    'Unhandled symbol layer type: %s' % type(sl),
                    'RT MapServer Exporter'
                )


    def serializeSimpleLineSymbolLayer(self, sl, hatchProperties=None):
        """Serialize a QGis simple line symbol layer into a MapServer style"""

        msStyle = mapscript.styleObj(self.msClass);

        # Line cap and line join
        msStyle.linecap = utils.serializePenCapStyle(sl.penCapStyle())
        msStyle.linejoin = utils.serializePenJoinStyle(sl.penJoinStyle())

        # If `hatchProperties` is a dict, we are serializing a line symbol layer inside a line
        # pattern fill, so we act accordingly and emit the respective properties.
        if isinstance(hatchProperties, dict):
            msStyle.symbolname = utils.serializeHatchSymbol(self.msMap) 
            msStyle.size = hatchProperties['size']
            msStyle.angle = hatchProperties['angle']
            msStyle.color = utils.serializeColor(sl.color())
        else:
            msStyle.outlinecolor = utils.serializeColor(sl.color())
       
        # Emit line pattern only if we have a non-solid pen
        if sl.penStyle() != Qt.NoPen and sl.penStyle() != Qt.SolidLine:
            utils.setPenStylePattern(msStyle, utils.serializePenStylePattern(sl))

        msStyle.width = 0 \
            if sl.penStyle() == Qt.NoPen \
            else utils.sizeUnitToPx(sl.width(), sl.widthUnit())

        # Assume that this is our only outline and set the layer's size units to map units
        # if we are using map units in QGis. This breaks every property with a size unit set to
        # anything other than the map unit.
        if (sl.width() > 0) and (hatchProperties == None):
            utils.maybeSetLayerSizeUnitFromMap(sl.widthUnit(), self.msLayer)


    def serializeSimpleFillSymbolLayer(self, sl):
        """Serialize a QGis simple fill symbol layer into MapServer styles"""

        msStyleBg = mapscript.styleObj(self.msClass)
        msStyleBg.angle = sl.angle()
        msStyleBg.color = utils.serializeColor(sl.fillColor())
        msStyleBg.opacity = int((sl.fillColor().alpha() / 255.0) * 100)

        # Only serialize outline if we have one
        if sl.borderStyle() != Qt.NoPen:
            msStyleOutline = mapscript.styleObj(self.msClass)
            msStyleOutline.outlinecolor = utils.serializeColor(sl.borderColor())

            # QGis draws a default outline of .26mm (roughly 1px) even when the width is set to zero
            msStyleOutline.width = utils.sizeUnitToPx(sl.borderWidth(), sl.borderWidthUnit()) \
                    if sl.borderWidth() > 0 \
                    else utils.DEFAULT_OUTLINE_WIDTH

            # Assume that this is our only outline and set the layer's size units to map units
            # if we are using map units in QGis. This breaks every property with a size unit set to
            # anything other than the map unit.
            if (sl.borderWidth() > 0):
                utils.maybeSetLayerSizeUnitFromMap(sl.borderWidthUnit(), self.msLayer)

            # Emit line pattern only if we have a non-solid pen
            if sl.borderStyle() != Qt.SolidLine:
                utils.setPenStylePattern(msStyleOutline, utils.serializePenStylePattern(sl))

    
    def serializeSimpleMarkerSymbolLayer(self, sl, fillProperties=None):
        """Serialize a QGis simple marker symbol layer into MapServer styles"""

        # Emit fill only if it's visible and the marker is polygonal
        markerName = unicode(sl.name()).encode('utf-8')
        if (sl.fillColor().alpha() != 0) and utils.isWellKnownMarkerPolygonal(markerName):
            msFillSymbol = utils.serializeWellKnownMarker(markerName, True)
            self.msMap.symbolset.appendSymbol(msFillSymbol) 

            msStyleBg = mapscript.styleObj(self.msClass)
            msStyleBg.symbolname = msFillSymbol.name
            msStyleBg.color = utils.serializeColor(sl.fillColor())
            msStyleBg.size = utils.sizeUnitToPx(sl.size(), sl.sizeUnit())

            # If `fillProperties` is a dict, we are serializing a marker symbol layer inside a point
            # pattern fill, so we act accordingly and emit the respective properties.
            if isinstance(fillProperties, dict):
                msStyleBg.gap = (fillProperties['distanceX'] + fillProperties['distanceY']) / 2
                msStyleBg.angle = fillProperties['angle']

        # Emit outline only if the marker has one
        if sl.outlineStyle() != Qt.NoPen:
            msOutlineSymbol = utils.serializeWellKnownMarker(markerName, False)
            self.msMap.symbolset.appendSymbol(msOutlineSymbol)

            msStyleOutline = mapscript.styleObj(self.msClass)
            msStyleOutline.symbolname = msOutlineSymbol.name
            msStyleOutline.color = utils.serializeColor(sl.borderColor())

            # QGis draws a default outline of .26mm even when the width is set to zero
            msStyleOutline.width = utils.sizeUnitToPx(sl.outlineWidth(), sl.outlineWidthUnit()) \
                    if sl.outlineWidth() > 0 \
                    else utils.DEFAULT_OUTLINE_WIDTH
            msStyleOutline.size = utils.sizeUnitToPx(sl.size(), sl.sizeUnit())

            # If `fillProperties` is a dict, we are serializing a marker symbol layer inside a point
            # pattern fill, so we act accordingly and emit the respective properties.
            if isinstance(fillProperties, dict):
                msStyleOutline.gap = (fillProperties['distanceX'] + fillProperties['distanceY']) / 2
                msStyleOutline.angle = fillProperties['angle']

            if sl.outlineStyle() != Qt.SolidLine:
                utils.setPenStylePattern(msStyleOutline, utils.serializePenStylePattern(sl))


    def serializeSvgMarkerSymbolLayer(self, sl):
        """Serialize a QGis SVG marker symbol layer into a MapServer style
        
        """
        try:
            msSymbol = utils.serializeSvgSymbol(unicode(sl.path()).encode('utf-8'))
        except Exception as e:
            QgsMessageLog.logMessage(
                u'Cannot serialize SVG symbol: %s' % unicode(e),
                'RT MapServer Exporter'
            )
            return

        self.msMap.symbolset.appendSymbol(msSymbol)

        msStyle = mapscript.styleObj(self.msClass)
        msStyle.symbolname = msSymbol.name
        msStyle.size = utils.sizeUnitToPx(sl.size(), sl.sizeUnit())


    def serializeFontMarkerSymbolLayer(self, sl):
        """Serialize a QGis font marker symbol layer into a MapServer style"""

        msSymbol = mapscript.symbolObj(utils.makeSymbolUUID('truetype'))
        msSymbol.type = mapscript.MS_SYMBOL_TRUETYPE
        msSymbol.filled = True
        msSymbol.inmapfile = True

        # Add font name to symbol object
        msSymbol.font = unicode(sl.fontFamily()).encode('utf-8')
        char = unicode(sl.character()).encode('utf-8')
        msSymbol.character = char

        self.msMap.symbolset.appendSymbol(msSymbol)

        msStyle = mapscript.styleObj(self.msClass)
        msStyle.symbolname = msSymbol.name
        msStyle.color = utils.serializeColor(sl.color())
        msStyle.size = utils.sizeUnitToPx(sl.size(), sl.sizeUnit())


    def serializeLinePatternFillSymbolLayer(self, sl):
        """Serialize a QGis line pattern fill symbol layer into MapServer styles"""

        for i in range(0, sl.subSymbol().symbolLayerCount()):
            ssl = sl.subSymbol().symbolLayer(i)

            if isinstance(ssl, QgsSimpleLineSymbolLayerV2):
                self.serializeSimpleLineSymbolLayer(
                    ssl,
                    {
                        'size': utils.sizeUnitToPx(sl.distance(), sl.distanceUnit()),
                        'angle': sl.lineAngle()
                    }
                )

    def serializePointPatternFillSymbolLayer(self, sl):
        """Serialize a QGis point pattern fill symbol layer into MapServer styles"""

        for i in range(0, sl.subSymbol().symbolLayerCount()):
            ssl = sl.subSymbol().symbolLayer(i)

            if isinstance(ssl, QgsSimpleMarkerSymbolLayerV2):
                # Displacements and different x-y distances are not currently supported on point
                # pattern fills. We pass them here though as they might be used in the future.
                self.serializeSimpleMarkerSymbolLayer(
                    ssl,
                    {
                        'distanceX': utils.sizeUnitToPx(sl.distanceX(), sl.distanceXUnit()),
                        'distanceY': utils.sizeUnitToPx(sl.distanceY(), sl.distanceYUnit()),
                        'displacementX': utils.sizeUnitToPx(sl.displacementX(), sl.displacementXUnit()),
                        'displacementY': utils.sizeUnitToPx(sl.displacementY(), sl.displacementYUnit()),
                        'angle': ssl.angle()
                    }
                )
