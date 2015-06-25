import os
import re
import string
import codecs
import binascii
import random
from tempfile import mkstemp

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import mapscript

"""Default outline width in pixels"""
DEFAULT_OUTLINE_WIDTH = 1


"""Qt -> MasServer pen styles
    (As per https://github.com/qgis/QGIS/blob/master/src/core/symbology-ng/qgssymbollayerv2utils.cpp)
"""
PEN_STYLE_MAP = {
    Qt.DashLine:       [4, 2],
    Qt.DotLine:        [1, 2],
    Qt.DashDotLine:    [4, 2, 1, 2],
    Qt.DashDotDotLine: [4, 2, 1, 2, 1, 2]
}


"""Qt -> Mapserver pen cap styles"""
PEN_CAP_STYLE_MAP = {
    Qt.FlatCap:   mapscript.MS_CJC_BUTT,
    Qt.RoundCap:  mapscript.MS_CJC_ROUND,
    Qt.SquareCap: mapscript.MS_CJC_SQUARE
}


"""Qt -> MapServer pen join styles"""
PEN_JOIN_STYLE_MAP = {
    Qt.BevelJoin: mapscript.MS_CJC_BEVEL,
    Qt.MiterJoin: mapscript.MS_CJC_MITER,
    Qt.RoundJoin: mapscript.MS_CJC_ROUND 
}


"""Vector representations of a subset of QGis' Simple Markers.

    You might notice that these are the same symbols that are supported by the SLD standard.
    Please note however, that the indexes here correspond to names used in QGis not those used in
    SLD.
"""
WELL_KNOWN_MARKER_MAP = {
    'rectangle':        [[0, 0],        [0, 1],         [1, 1],     [1, 0],         [0, 0]],
    'triangle':         [[0, 1],        [0.5, 0],       [1, 1],     [0, 1]],
    'regular_star':     [[0, 0.375],    [0.35, 0.375],  [0.5, 0],   [0.65, 0.375],  [1, 0.375],
                         [0.75, 0.625], [0.875, 1],     [0.5, 0.75],[0.125, 1],     [0.25, 0.625],
                         [0, 0.375]],
    'cross':            [[0.5, 0],      [0.5, 1],       [-99, 99],  [0, 0.5],       [1, 0.5]],
    'cross2':           [[0, 0],        [1, 1],         [-99, 99],  [0, 1],         [1, 0]]
}


"""Markers that do not have closed areas (i.e. cannot have fills)"""
LINEAL_WELL_KNOWN_MARKERS = ['cross', 'cross2']


"""QGis -> MapServer label position constants"""
LABEL_POSITION_MAP = {
    QgsPalLayerSettings.QuadrantAboveLeft:  mapscript.MS_UL,
    QgsPalLayerSettings.QuadrantAbove:      mapscript.MS_UC,
    QgsPalLayerSettings.QuadrantAboveRight: mapscript.MS_UR,
    QgsPalLayerSettings.QuadrantLeft:       mapscript.MS_CL,
    QgsPalLayerSettings.QuadrantOver:       mapscript.MS_CC,
    QgsPalLayerSettings.QuadrantRight:      mapscript.MS_CR,
    QgsPalLayerSettings.QuadrantBelowLeft:  mapscript.MS_LL,
    QgsPalLayerSettings.QuadrantBelow:      mapscript.MS_LC,
    QgsPalLayerSettings.QuadrantBelowRight: mapscript.MS_LR
}

"""Default path for extracted SVG images"""
SVG_IMAGE_DIR = 'svgrasters'

def mmToPx(mm):
    """Convert millimeters to pixels (assuming an 72dpi display)"""

    return mm * 3.779527559


def ptToPx(pt):
    """Convert points to pixels (assuming an 72dpi display)"""

    return pt * 96 / 72


def makeSymbolUUID(prefix=''):
    """Generate a globally unique identifier to be used in symbol names"""

    return prefix + '_' + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))


def serializeColor(qColor):
    """Serialize a QColor() into a mapscript.colorObj()"""

    msColor = mapscript.colorObj(qColor.red(), qColor.green(), qColor.blue(), qColor.alpha())
    return msColor

def setPenStylePattern(style, pattern):
    """Set the PATTERN clause on a MapServer Style
    
        Please note that before MapServer version 7 it is impossible to set the `pattern`
        property on `styleObj`s.
        In MapServer 6.4 we use a workaround that involves manually adding the PATTERN clause
        to the style. This does not work in previous versions as the `styleObj.convertToString()`
        was added in MapServer 6.4
        (see http://mapserver.org/tr/mapscript/mapscript.html#styleobj-methods).

        Relevant MapServer bug:
            https://github.com/mapserver/mapserver/issues/4943
    """

    if mapscript.MS_VERSION_MAJOR == 7:
        style.pattern = pattern

    elif (mapscript.MS_VERSION_MAJOR == 6) and (mapscript.MS_VERSION_MINOR >= 4):
        patternStr = "\nPATTERN %s END\nEND" % ' '.join(map(str, pattern))
        styleStr = style.convertToString().rsplit('END', 1)

        style.updateFromString('%s%s%s' % (styleStr[0], patternStr, styleStr[1]))

    else:
        QgsMessageLog.logMessage(
            'Line patterns are only supported in MapServer versions 6.4 and above.',
            'RT MapServer Exporter'
        )

        

def serializePenStylePattern(sl):
    """Serialize the Qt.PenStyle() of a symbol layer's outline/border into mapscript form"""

    if hasattr(sl, 'penStyle'):
        return map(mmToPx, PEN_STYLE_MAP[sl.penStyle()]) \
            if sl.penStyle() != Qt.CustomDashLine \
            else sl.customDashVector()
    elif hasattr(sl, 'borderStyle'):
        return map(mmToPx, PEN_STYLE_MAP[sl.borderStyle()])
    else:
        return map(mmToPx, PEN_STYLE_MAP[sl.outlineStyle()])


def serializePenJoinStyle(pjs):
    """Serialize a Qt.PenJoinStyle into mapscript form"""

    return PEN_JOIN_STYLE_MAP[pjs]


def serializePenCapStyle(pcs):
    """Serialize a Qt.PenCapStyle into mapscript form"""

    return PEN_CAP_STYLE_MAP[pcs]

def serializeHatchSymbol(msMap):
    """Create a per-mapfile singleton hatch symbol

        HATCH symbols in MapServer do not have any attributes other than their name and type,
        so a single instance is sufficient for all our needs.

        This is a bit of a hack relying on the fact that you can set whatever attributes you want
        on SWIG objects. Therefore we save the symbol name directly into the `mapObject`.
    """

    if not hasattr(msMap, 'singletonHatchSymbolName'):
        hatchSymbol = mapscript.symbolObj(makeSymbolUUID('hatch'))
        hatchSymbol.type = mapscript.MS_SYMBOL_HATCH
        hatchSymbol.inmapfile = True

        msMap.symbolset.appendSymbol(hatchSymbol)
        msMap.singletonHatchSymbolName = hatchSymbol.name

    return msMap.singletonHatchSymbolName


def serializeSvgSymbol(svgPath):
    """Serialize an SVG symbol into a mapscript.symbolObj()

        We have a couple of problems here though:

        1. SVGs with embedded raster images

            As MapServer seems to be unable to handle SVG files with an embedded <image />, we use
            some magic here to extract said image into a separate file and use a pixmap symbol
            instead. Please note the following:
                a. We only consider the first embedded image in the SVG file.
                b. Embedded images are saved to the directory the SVG file resides in.

        2. As it is currently (MapServer 7.0.0-beta) impossible to set the `imagepath` attribute on
           a symbolObj() we use a workaround that involves manually writing, then re-parsing
           a symbol set definition file.

            Possibly relevant MapServer bugs:
                https://github.com/mapserver/mapserver/issues/4501
                https://github.com/mapserver/mapserver/issues/5074
                https://github.com/mapserver/mapserver/issues/5109
    """

    # Check if the SVG file contains an embedded image
    with codecs.open(svgPath, 'r', 'utf-8') as fin:
        svgContents = fin.read().replace('\n', '')
    
    rx = re.compile(u'<image[^>]+xlink:href="([^"]+)"')
    m = rx.search(svgContents)

    if (m is not None):
        # We have an image, check if its a data URI or a general one
        uri = m.group(1)
        imageType = 'PIXMAP'
        symbolUUID = makeSymbolUUID('svgraster')

        if uri[:10] == u'data:image':
            # We have a data URI, save the image into an external file.
            # Please note that we only consider base64-encoded images here.
            #
            dataURIRx = re.compile('data:image/(\w+);base64,(.+)')
            dm = dataURIRx.match(uri)

            if (dm is not None):
                imageExt = dm.group(1)
                try:
                    imageData = bytearray(binascii.a2b_base64(dm.group(2)))
                except:
                    raise ValueError('Cannot decode base64 URI in embedded image while parsing SVG.') 
                
                imageName = '%s.%s' % (symbolUUID, imageExt)
                imageDir = os.path.join(os.path.dirname(svgPath), SVG_IMAGE_DIR)
                
                if not os.path.exists(imageDir):
                    os.makedirs(imageDir)

                imagePath = os.path.join(imageDir, imageName).encode('utf-8')

                with open(imagePath, 'wb') as imageOut:
                    imageOut.write(imageData)

            else:
                raise ValueError('Invalid data URI encountered while parsing SVG.')
            
        else:
            # We have a non-data URI.
            # We only want to consider relative URIs here so perform some naive sanity checks on it

            if uri.startswith('file://'):
                uri = uri[7:]
                if (uri.find('..') == -1) and (not uri.startswith('/')):
                    imagePath = os.path.join(os.path.dirname(svgPath), uri)
                else:
                    raise ValueError('Invalid URI encountered while parsing SVG.')
            else:
                raise ValueError('Invalid URI encountered while parsing SVG.')
    else:
        # We do not have an embedded image thus the SVG is all vector and can probably be 
        # rendered without a hitch

        imageType = 'SVG' 
        imagePath = svgPath

    symbolSetData = """
        SYMBOLSET
            SYMBOL
                NAME "%s"
                TYPE %s
                IMAGE "%s"
                ANCHORPOINT 0.5 0.5
            END
        END
    """

    # Create a temporary file and open it
    (tempHandle, tempName) = mkstemp()
    
    # Write symbol set data
    os.write(tempHandle, symbolSetData % (makeSymbolUUID('svg'), imageType, imagePath))
    os.close(tempHandle)

    # Load and parse the symbol set
    msSymbolSet = mapscript.symbolSetObj(tempName)

    # Remove the temporary file
    # os.unlink(tempName)

    # Fetch and return our SVG symbol
    msSymbol = msSymbolSet.getSymbol(1)
    msSymbol.inmapfile = True

    return msSymbol


def isWellKnownMarker(marker):
    """Check if a marker's name matches our list of well known markers"""

    return marker in WELL_KNOWN_MARKER_MAP


def isWellKnownMarkerPolygonal(marker):
    """Check if a well known marker is polygonal (i.e. may have a fill)"""

    return marker not in LINEAL_WELL_KNOWN_MARKERS


def serializeWellKnownMarker(marker, filled):
    """Serialize a well known marker into a mapscript.symbolObj()"""

    msSymbol = mapscript.symbolObj('%s' % (makeSymbolUUID(marker)))
    msSymbol.type = mapscript.MS_SYMBOL_VECTOR
    msSymbol.inmapfile = True
    msLine = mapscript.lineObj()

    def setPoints(ps):
        """Set the points of the marker"""

        for p in ps:
            msLine.add(mapscript.pointObj(p[0], p[1]))

        msSymbol.setPoints(msLine)

    if isWellKnownMarker(marker):
        setPoints(WELL_KNOWN_MARKER_MAP[marker])
        mayHaveFill = isWellKnownMarkerPolygonal(marker)
    else:
        # We use a simple circle if the marker is not among our currently known markers
        msSymbol.type = mapscript.MS_SYMBOL_ELLIPSE
        setPoints([[1, 1]])
        mayHaveFill = True

    msSymbol.filled = mayHaveFill and filled

    return msSymbol


def serializeLabelPosition(ps):
    """Serialize a label's position to MapServer"""

    if ps.placement == QgsPalLayerSettings.AroundPoint:
        return mapscript.MS_AUTO

    return LABEL_POSITION_MAP[ps.quadOffset] \
            if ps.quadOffset in LABEL_POSITION_MAP \
            else mapscript.MS_AUTO


def serializeFontDefinition(font, style):
    """Serialize a font definition and a font size to MapServer"""

    family = font.family().replace(' ', '')
    style = style.replace(' ', '')

    if style == '*':
        fontDef = family
    else:
        fontDef = '%s-%s' % (family, style)

    fm = QFontMetrics(font)

    return (unicode(fontDef).encode('utf8'), fm.height())
