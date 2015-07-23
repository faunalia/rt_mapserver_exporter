# rt_mapserver_exporter
Export a QGIS project to MapFile

What you see is now is the fork of Faunalia's orginal plugin:
https://github.com/faunalia/rt_mapserver_exporter

## This plugin still has considerable limitation mainly due to the differences between the QGIS and mapserver rendering engine and the specific use we intend to use it for.

### Corrections and changes to the original:
TBD

### Some of the limitations:
- Permanently adds to mapfile: PROCESSING "LABEL_NO_CLIP=ON" and PARTIALS=FALSE on EVERY labelled feature as we use this in a tiled environment. QGIS API has QgsPalLabeling::isShowingPartialsLabels but could not find it on the QGIS style setting GUI. These probably need some more user control over them.
- Mapfile's SIZEUNITS is determined by the first occurence of "Map unit" vs. "Millimeter" in the QGIS style definition. In mapserver this is a LAYER property, in QGIS one can set it for every style property so expect differences here apart from very simple cases.
- To get fill patterns work you need to use "Line pattern fill". Other type of hatches and patterns will result in a uniform fill.
- Font names are exported to match the locale of the box doing the export. fonts file must be assembled keeping this in mind. Check the resulting mapfile to see actual font names exported.

Big thanks to authors of original plugin:
- Luigi Pirelli
- Paolo Cavallini
- Giuseppe Sucameli

