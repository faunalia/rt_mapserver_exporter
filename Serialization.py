import mapscript
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

import SerializationUtils as utils

class LabelStyleSerializer(object):
    def __init__(self, layer, msLayer, msMap, emitFontDefinitions=False):
        """Serialize labels of a QGis vector layer to mapscript"""

        self.layer = layer
        self.msLayer = msLayer
        self.msMap = msMap

        labelingEngine = QgsPalLabeling()

        if labelingEngine and labelingEngine.willUseLayer(self.layer):
            ps = QgsPalLayerSettings.fromLayer(self.layer)

            if not ps.isExpression:
                self.msLayer.labelitem = str(ps.fieldName)
            else:
                pass

            msLabel = mapscript.labelObj()

            msLabel.type = mapscript.MS_TRUETYPE
           
            # Position, rotation and scaling
            msLabel.position = utils.serializeLabelPosition(ps)
            msLabel.offsetx = int(ps.xOffset)
            msLabel.offsety = int(ps.yOffset)

            # Data defined rotation
            # Please note that this is the only currently supported data defined property.
            if QgsPalLayerSettings.Rotation in ps.dataDefinedProperties.keys():
                dd = ps.dataDefinedProperty(QgsPalLayerSettings.Rotation)
                rotField = str(dd.field())
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
            if emitFontDefinitions == True:
                msLabel.font = fontDef

            # Font size and color
            msLabel.color = utils.serializeColor(ps.textColor)

            if ps.fontLimitPixelSize:
                msLabel.minsize = ps.fontMinPixelSize
                msLabel.maxsize = ps.fontMaxPixelSize

            # Other properties
            msLabel.wrap = str(ps.wrapChar)
            msLabel.priority = ps.priority
            msLabel.buffer = int(utils.mmToPx(ps.bufferSize))

            if ps.minFeatureSize > 0:
                msLabel.minfeaturesize = utils.mmToPx(ps.minFeatureSize)

            # Label definitions gets appended to the very first class on a layer, or to a new class
            # if no classes exist.
            msClass = msLayer.getClass(0) \
                if (msLayer.numclasses > 0) \
                else mapscript.classObj(msLayer)

            msClass.addLabel(msLabel)


            
class VectorLayerStyleSerializer(object):
    def __init__(self, layer, msLayer, msMap):
        """Serialize a QGis vector layer renderer into mapscript classes"""

        self.msLayer = msLayer
        self.msMap = msMap

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

        for sym in renderer.symbols():
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
            cv = cv.toString() if isinstance(cv, QVariant) else str(cv)

            msClass.setExpression(u'("[%s]" = "%s")' % (attr, cv))
            SymbolLayerSerializer(renderer.symbols()[i], msClass, self.msLayer, self.msMap)
            i = i + 1


    def serializeGraduatedSymbolRenderer(self, renderer):
        """Serialize a QGis graduated symbol renderer into MapServer classes"""

        attr = renderer.usedAttributes()[0]
        i = 0

        for range in renderer.ranges():
            msClass = mapscript.classObj(self.msLayer)

            # We use '>=' instead of '>' when defining the first class to also include the lowest
            # value of the range in the expression.
            msClass.setExpression(u'(([%s] %s %f) And ([%s] <= %f))' % ( \
                attr, \
                '>=' if (i == 0) else '>', \
                range.lowerValue(), \
                attr, \
                range.upperValue() \
            ))
            SymbolLayerSerializer(renderer.symbols()[i], msClass, self.msLayer, self.msMap)
            i = i + 1



class SymbolLayerSerializer(object):
    def __init__(self, sym, msClass, msLayer, msMap):
        """Serialize a QGis symbol layer into a MapServer style"""
        
        self.msClass = msClass
        self.msLayer = msLayer
        self.msMap = msMap

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
            msStyle.pattern = utils.serializePenStylePattern(sl)

        msStyle.width = 0 if sl.penStyle() == Qt.NoPen else utils.mmToPx(sl.width())


    def serializeSimpleFillSymbolLayer(self, sl):
        """Serialize a QGis simple fill symbol layer into MapServer styles"""

        msStyleBg = mapscript.styleObj(self.msClass)
        msStyleBg.angle = sl.angle()
        msStyleBg.color = utils.serializeColor(sl.fillColor())

        # Only serialize outline if we have one
        if sl.borderStyle() != Qt.NoPen:
            msStyleOutline = mapscript.styleObj(self.msClass)
            msStyleOutline.outlinecolor = utils.serializeColor(sl.borderColor())

            # QGis draws a default outline of .26mm (roughly 1px) even when the width is set to zero
            msStyleOutline.width = utils.mmToPx(sl.borderWidth()) \
                    if sl.borderWidth() > 0 \
                    else utils.DEFAULT_OUTLINE_WIDTH

            # Emit line pattern only if we have a non-solid pen
            if sl.borderStyle() != Qt.SolidLine:
                msStyleOutline.pattern = utils.serializePenStylePattern(sl)

    
    def serializeSimpleMarkerSymbolLayer(self, sl, fillProperties=None):
        """Serialize a QGis simple marker symbol layer into MapServer styles"""

        # Emit fill only if it's visible and the marker is polygonal 
        if (sl.fillColor().alpha() != 0) and utils.isWellKnownMarkerPolygonal(str(sl.name())):
            msFillSymbol = utils.serializeWellKnownMarker(str(sl.name()), True)
            self.msMap.symbolset.appendSymbol(msFillSymbol) 

            msStyleBg = mapscript.styleObj(self.msClass)
            msStyleBg.symbolname = msFillSymbol.name
            msStyleBg.color = utils.serializeColor(sl.fillColor())
            msStyleBg.size = utils.mmToPx(sl.size())

            # If `fillProperties` is a dict, we are serializing a marker symbol layer inside a point
            # pattern fill, so we act accordingly and emit the respective properties.
            if isinstance(fillProperties, dict):
                msStyleBg.gap = (fillProperties['distanceX'] + fillProperties['distanceY']) / 2
                msStyleBg.angle = fillProperties['angle']

        # Emit outline only if the marker has one
        if sl.outlineStyle() != Qt.NoPen:
            msOutlineSymbol = utils.serializeWellKnownMarker(str(sl.name()), False)
            self.msMap.symbolset.appendSymbol(msOutlineSymbol)

            msStyleOutline = mapscript.styleObj(self.msClass)
            msStyleOutline.symbolname = msOutlineSymbol.name
            msStyleOutline.color = utils.serializeColor(sl.borderColor())

            # QGis draws a default outline of .26mm even when the width is set to zero
            msStyleOutline.width = utils.mmToPx(sl.outlineWidth()) \
                    if sl.outlineWidth() > 0 \
                    else utils.DEFAULT_OUTLINE_WIDTH
            msStyleOutline.size = utils.mmToPx(sl.size())

            # If `fillProperties` is a dict, we are serializing a marker symbol layer inside a point
            # pattern fill, so we act accordingly and emit the respective properties.
            if isinstance(fillProperties, dict):
                msStyleOutline.gap = (fillProperties['distanceX'] + fillProperties['distanceY']) / 2
                msStyleOutline.angle = fillProperties['angle']

            if sl.outlineStyle() != Qt.SolidLine:
                msStyleOutline.pattern = utils.serializePenStylePattern(sl)


    def serializeSvgMarkerSymbolLayer(self, sl):
        """Serialize a QGis SVG marker symbol layer into a MapServer style"""

        msSymbol = utils.serializeSvgSymbol(str(sl.path()))
        self.msMap.symbolset.appendSymbol(msSymbol)

        msStyle = mapscript.styleObj(self.msClass)
        msStyle.symbolname = msSymbol.name
        msStyle.size = utils.mmToPx(sl.size())


    def serializeFontMarkerSymbolLayer(self, sl):
        """Serialize a QGis font marker symbol layer into a MapServer style"""

        msSymbol = mapscript.symbolObj(utils.makeSymbolUUID('truetype'))
        msSymbol.type = mapscript.MS_SYMBOL_TRUETYPE
        msSymbol.filled = True
        msSymbol.character = str(sl.character())
        msSymbol.inmapfile = True

        self.msMap.symbolset.appendSymbol(msSymbol)

        msStyle = mapscript.styleObj(self.msClass)
        msStyle.symbolname = msSymbol.name
        msStyle.color = utils.serializeColor(sl.color())
        msStyle.size = utils.mmToPx(sl.size())


    def serializeLinePatternFillSymbolLayer(self, sl):
        """Serialize a QGis line pattern fill symbol layer into MapServer styles"""

        for i in range(0, sl.subSymbol().symbolLayerCount()):
            ssl = sl.subSymbol().symbolLayer(i)

            if isinstance(ssl, QgsSimpleLineSymbolLayerV2):
                self.serializeSimpleLineSymbolLayer(
                    ssl,
                    {
                        'size': utils.mmToPx(sl.distance()),
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
                        'distanceX': utils.mmToPx(sl.distanceX()),
                        'distanceY': utils.mmToPx(sl.distanceY()),
                        'displacementX': utils.mmToPx(sl.displacementX()),
                        'displacementY': utils.mmToPx(sl.displacementY()),
                        'angle': sl.angle()
                    }
                )
