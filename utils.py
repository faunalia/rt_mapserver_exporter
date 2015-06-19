import mapscript
import utils
from qgis.core import *

def toUTF8(s):
    return unicode(s).encode('utf8')

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

def getLayerType(layer):
    if layer.type() == QgsMapLayer.RasterLayer:
            return mapscript.MS_LAYER_RASTER
    if layer.geometryType() == QGis.Point:
            return mapscript.MS_LAYER_POINT
    if layer.geometryType() == QGis.Line:
            return mapscript.MS_LAYER_LINE
    if layer.geometryType() == QGis.Polygon:
            return mapscript.MS_LAYER_POLYGON
