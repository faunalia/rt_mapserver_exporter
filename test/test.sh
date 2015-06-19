#!/bin/sh

# Environment variables
SCRIPT=$(readlink -f "$0")
BASEDIR=$(dirname "$(readlink -f "$0")")
PLUGIN_DIR=~/.qgis2/python/plugins
PYTHONPATH=/usr/share/qgis/python:/usr/lib/python2.7:/usr/lib/python2.7/site-packages:${PLUGIN_DIR}
CUSTOM_LOCALE=C

# Binaries

PYTHON=python2
TEST_SCRIPT="${BASEDIR}"/test.py
SHP2IMG=shp2img
PREVIEWER=xdg-open

# `shp2img` arguments
MAPFILE="${BASEDIR}"/test.map
OUTFILE="${BASEDIR}"/test.png
DEBUG_LEVEL=5

# Force python to recompile the plugin
rm "${PLUGIN_DIR}"/rt_mapserver_exporter/*.pyc

# Run tests as a standalone PyQGis application
#
# Please note the following:
#   - The currently applied locale affects how mapscript handles numeric formatting.
#     This may cause issues when mapfiles are output while a locale with a decimal separator other
#     than '.' is set. (See MapServer bug #1762: https://trac.osgeo.org/mapserver/ticket/1762)
#     To ensure the former never happens we temporarily reset the locale to the default ('C') one
#     before running python.
#
#	- All command line arguments are passed along to the python binary so that we can for example
#	  break into the REPL with `$0 -i` after running tests (useful for debugging).
LC_NUMERIC=${CUSTOM_LOCALE} PYTHONPATH="${PYTHONPATH}" ${PYTHON} "${@}" "${TEST_SCRIPT}"

# Run `shp2img` to generate an image from the mapfile
${SHP2IMG} \
	-m "${MAPFILE}" \
	-o "${OUTFILE}" \
	--all_debug "${DEBUG_LEVEL}" \
	--map_debug "${DEBUG_LEVEL}"

# Open the output image in a previewer if python was not running in interactive mode (e. g. debugging).
if [[ $1 != "-i" ]]; then
	${PREVIEWER} "${OUTFILE}"
fi
