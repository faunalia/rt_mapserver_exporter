# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/mnt/data/PROGRAMMING/FAUNALIA/qgis-plugins/rt_mapserver_exporter/ui/mapfileexportdlg.ui'
#
# Created: Fri Mar 28 09:55:24 2014
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MapfileExportDlg(object):
    def setupUi(self, MapfileExportDlg):
        MapfileExportDlg.setObjectName(_fromUtf8("MapfileExportDlg"))
        MapfileExportDlg.resize(547, 483)
        MapfileExportDlg.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(MapfileExportDlg)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.buttonBox = QtGui.QDialogButtonBox(MapfileExportDlg)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Help|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 2)
        self.tabWidget = QtGui.QTabWidget(MapfileExportDlg)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.gridLayout_3 = QtGui.QGridLayout(self.tab)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.btnChooseFile = QtGui.QToolButton(self.tab)
        self.btnChooseFile.setObjectName(_fromUtf8("btnChooseFile"))
        self.gridLayout_3.addWidget(self.btnChooseFile, 0, 2, 1, 1)
        self.txtMapFilePath = QtGui.QLineEdit(self.tab)
        self.txtMapFilePath.setText(_fromUtf8(""))
        self.txtMapFilePath.setObjectName(_fromUtf8("txtMapFilePath"))
        self.gridLayout_3.addWidget(self.txtMapFilePath, 0, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_3.addItem(spacerItem, 3, 0, 1, 3)
        self.label = QtGui.QLabel(self.tab)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 1)
        self.grpMap = QtGui.QGroupBox(self.tab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.grpMap.sizePolicy().hasHeightForWidth())
        self.grpMap.setSizePolicy(sizePolicy)
        self.grpMap.setObjectName(_fromUtf8("grpMap"))
        self.gridLayout_2 = QtGui.QGridLayout(self.grpMap)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label1 = QtGui.QLabel(self.grpMap)
        self.label1.setToolTip(_fromUtf8(""))
        self.label1.setObjectName(_fromUtf8("label1"))
        self.gridLayout_2.addWidget(self.label1, 0, 0, 1, 1)
        self.label5 = QtGui.QLabel(self.grpMap)
        self.label5.setIndent(20)
        self.label5.setObjectName(_fromUtf8("label5"))
        self.gridLayout_2.addWidget(self.label5, 0, 4, 1, 1)
        self.cmbMapImageType = QtGui.QComboBox(self.grpMap)
        self.cmbMapImageType.setObjectName(_fromUtf8("cmbMapImageType"))
        self.gridLayout_2.addWidget(self.cmbMapImageType, 0, 5, 1, 1)
        self.label2 = QtGui.QLabel(self.grpMap)
        self.label2.setObjectName(_fromUtf8("label2"))
        self.gridLayout_2.addWidget(self.label2, 1, 0, 1, 1)
        self.txtMapWidth = QtGui.QLineEdit(self.grpMap)
        self.txtMapWidth.setText(_fromUtf8("600"))
        self.txtMapWidth.setObjectName(_fromUtf8("txtMapWidth"))
        self.gridLayout_2.addWidget(self.txtMapWidth, 1, 1, 1, 1)
        self.label3 = QtGui.QLabel(self.grpMap)
        self.label3.setIndent(20)
        self.label3.setObjectName(_fromUtf8("label3"))
        self.gridLayout_2.addWidget(self.label3, 1, 2, 1, 1)
        self.txtMapHeight = QtGui.QLineEdit(self.grpMap)
        self.txtMapHeight.setText(_fromUtf8("600"))
        self.txtMapHeight.setObjectName(_fromUtf8("txtMapHeight"))
        self.gridLayout_2.addWidget(self.txtMapHeight, 1, 3, 1, 1)
        self.label4 = QtGui.QLabel(self.grpMap)
        self.label4.setEnabled(False)
        self.label4.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label4.setObjectName(_fromUtf8("label4"))
        self.gridLayout_2.addWidget(self.label4, 1, 4, 1, 1)
        self.cmbMapUnits = QtGui.QComboBox(self.grpMap)
        self.cmbMapUnits.setEnabled(False)
        self.cmbMapUnits.setObjectName(_fromUtf8("cmbMapUnits"))
        self.gridLayout_2.addWidget(self.cmbMapUnits, 1, 5, 1, 1)
        self.label6_2 = QtGui.QLabel(self.grpMap)
        self.label6_2.setMinimumSize(QtCore.QSize(80, 0))
        self.label6_2.setObjectName(_fromUtf8("label6_2"))
        self.gridLayout_2.addWidget(self.label6_2, 2, 0, 1, 1)
        self.txtMapShapePath = QtGui.QLineEdit(self.grpMap)
        self.txtMapShapePath.setText(_fromUtf8(""))
        self.txtMapShapePath.setObjectName(_fromUtf8("txtMapShapePath"))
        self.gridLayout_2.addWidget(self.txtMapShapePath, 2, 1, 1, 5)
        self.txtMapName = QtGui.QLineEdit(self.grpMap)
        self.txtMapName.setToolTip(_fromUtf8(""))
        self.txtMapName.setText(_fromUtf8("QGIS-MAP"))
        self.txtMapName.setObjectName(_fromUtf8("txtMapName"))
        self.gridLayout_2.addWidget(self.txtMapName, 0, 1, 1, 3)
        self.gridLayout_3.addWidget(self.grpMap, 1, 0, 1, 3)
        self.groupBox_2 = QtGui.QGroupBox(self.tab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout_4 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.label6 = QtGui.QLabel(self.groupBox_2)
        self.label6.setMinimumSize(QtCore.QSize(80, 0))
        self.label6.setObjectName(_fromUtf8("label6"))
        self.gridLayout_4.addWidget(self.label6, 0, 0, 1, 1)
        self.txtMapServerUrl = QtGui.QLineEdit(self.groupBox_2)
        self.txtMapServerUrl.setText(_fromUtf8("http://localhost/cgi-bin/mapserv"))
        self.txtMapServerUrl.setObjectName(_fromUtf8("txtMapServerUrl"))
        self.gridLayout_4.addWidget(self.txtMapServerUrl, 0, 1, 1, 1)
        self.label6_5 = QtGui.QLabel(self.groupBox_2)
        self.label6_5.setMinimumSize(QtCore.QSize(80, 0))
        self.label6_5.setObjectName(_fromUtf8("label6_5"))
        self.gridLayout_4.addWidget(self.label6_5, 1, 0, 1, 1)
        self.txtWebImagePath = QtGui.QLineEdit(self.groupBox_2)
        self.txtWebImagePath.setText(_fromUtf8(""))
        self.txtWebImagePath.setObjectName(_fromUtf8("txtWebImagePath"))
        self.gridLayout_4.addWidget(self.txtWebImagePath, 1, 1, 1, 1)
        self.label6_4 = QtGui.QLabel(self.groupBox_2)
        self.label6_4.setMinimumSize(QtCore.QSize(80, 0))
        self.label6_4.setObjectName(_fromUtf8("label6_4"))
        self.gridLayout_4.addWidget(self.label6_4, 3, 0, 1, 1)
        self.label6_7 = QtGui.QLabel(self.groupBox_2)
        self.label6_7.setMinimumSize(QtCore.QSize(80, 0))
        self.label6_7.setToolTip(_fromUtf8(""))
        self.label6_7.setObjectName(_fromUtf8("label6_7"))
        self.gridLayout_4.addWidget(self.label6_7, 4, 0, 1, 1)
        self.txtExternalGraphicRegexp = QtGui.QLineEdit(self.groupBox_2)
        self.txtExternalGraphicRegexp.setToolTip(_fromUtf8(""))
        self.txtExternalGraphicRegexp.setText(_fromUtf8(""))
        self.txtExternalGraphicRegexp.setObjectName(_fromUtf8("txtExternalGraphicRegexp"))
        self.gridLayout_4.addWidget(self.txtExternalGraphicRegexp, 4, 1, 1, 1)
        self.label6_6 = QtGui.QLabel(self.groupBox_2)
        self.label6_6.setMinimumSize(QtCore.QSize(80, 0))
        self.label6_6.setObjectName(_fromUtf8("label6_6"))
        self.gridLayout_4.addWidget(self.label6_6, 2, 0, 1, 1)
        self.txtWebImageUrl = QtGui.QLineEdit(self.groupBox_2)
        self.txtWebImageUrl.setText(_fromUtf8(""))
        self.txtWebImageUrl.setObjectName(_fromUtf8("txtWebImageUrl"))
        self.gridLayout_4.addWidget(self.txtWebImageUrl, 2, 1, 1, 1)
        self.txtWebTempPath = QtGui.QLineEdit(self.groupBox_2)
        self.txtWebTempPath.setToolTip(_fromUtf8(""))
        self.txtWebTempPath.setText(_fromUtf8(""))
        self.txtWebTempPath.setObjectName(_fromUtf8("txtWebTempPath"))
        self.gridLayout_4.addWidget(self.txtWebTempPath, 3, 1, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox_2, 2, 0, 1, 3)
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.gridLayout_7 = QtGui.QGridLayout(self.tab_2)
        self.gridLayout_7.setObjectName(_fromUtf8("gridLayout_7"))
        self.checkTmplFromFile = QtGui.QRadioButton(self.tab_2)
        self.checkTmplFromFile.setChecked(True)
        self.checkTmplFromFile.setObjectName(_fromUtf8("checkTmplFromFile"))
        self.gridLayout_7.addWidget(self.checkTmplFromFile, 0, 0, 1, 3)
        self.txtTemplatePath = QtGui.QLineEdit(self.tab_2)
        self.txtTemplatePath.setText(_fromUtf8("[templatepath]"))
        self.txtTemplatePath.setObjectName(_fromUtf8("txtTemplatePath"))
        self.gridLayout_7.addWidget(self.txtTemplatePath, 0, 3, 1, 1)
        self.btnChooseTemplate = QtGui.QToolButton(self.tab_2)
        self.btnChooseTemplate.setObjectName(_fromUtf8("btnChooseTemplate"))
        self.gridLayout_7.addWidget(self.btnChooseTemplate, 0, 4, 1, 1)
        self.checkGenerateTmpl = QtGui.QRadioButton(self.tab_2)
        self.checkGenerateTmpl.setObjectName(_fromUtf8("checkGenerateTmpl"))
        self.gridLayout_7.addWidget(self.checkGenerateTmpl, 1, 0, 1, 4)
        spacerItem1 = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.gridLayout_7.addItem(spacerItem1, 2, 0, 1, 1)
        self.templateTable = QtGui.QTableView(self.tab_2)
        self.templateTable.setEnabled(False)
        self.templateTable.setObjectName(_fromUtf8("templateTable"))
        self.gridLayout_7.addWidget(self.templateTable, 2, 1, 1, 4)
        self.label_2 = QtGui.QLabel(self.tab_2)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_7.addWidget(self.label_2, 3, 0, 1, 2)
        self.txtTmplHeaderPath = QtGui.QLineEdit(self.tab_2)
        self.txtTmplHeaderPath.setText(_fromUtf8(""))
        self.txtTmplHeaderPath.setObjectName(_fromUtf8("txtTmplHeaderPath"))
        self.gridLayout_7.addWidget(self.txtTmplHeaderPath, 3, 2, 1, 2)
        self.btnChooseTmplHeader = QtGui.QToolButton(self.tab_2)
        self.btnChooseTmplHeader.setObjectName(_fromUtf8("btnChooseTmplHeader"))
        self.gridLayout_7.addWidget(self.btnChooseTmplHeader, 3, 4, 1, 1)
        self.label_3 = QtGui.QLabel(self.tab_2)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_7.addWidget(self.label_3, 4, 0, 1, 2)
        self.txtTmplFooterPath = QtGui.QLineEdit(self.tab_2)
        self.txtTmplFooterPath.setText(_fromUtf8(""))
        self.txtTmplFooterPath.setObjectName(_fromUtf8("txtTmplFooterPath"))
        self.gridLayout_7.addWidget(self.txtTmplFooterPath, 4, 2, 1, 2)
        self.btnChooseTmplFooter = QtGui.QToolButton(self.tab_2)
        self.btnChooseTmplFooter.setObjectName(_fromUtf8("btnChooseTmplFooter"))
        self.gridLayout_7.addWidget(self.btnChooseTmplFooter, 4, 4, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_7.addItem(spacerItem2, 5, 0, 1, 5)
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName(_fromUtf8("tab_3"))
        self.gridLayout_8 = QtGui.QGridLayout(self.tab_3)
        self.gridLayout_8.setObjectName(_fromUtf8("gridLayout_8"))
        self.grpOptions = QtGui.QGroupBox(self.tab_3)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.grpOptions.sizePolicy().hasHeightForWidth())
        self.grpOptions.setSizePolicy(sizePolicy)
        self.grpOptions.setObjectName(_fromUtf8("grpOptions"))
        self.gridLayout_5 = QtGui.QGridLayout(self.grpOptions)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.checkBoxForce = QtGui.QCheckBox(self.grpOptions)
        self.checkBoxForce.setObjectName(_fromUtf8("checkBoxForce"))
        self.gridLayout_5.addWidget(self.checkBoxForce, 0, 0, 1, 1)
        self.checkBoxPartials = QtGui.QCheckBox(self.grpOptions)
        self.checkBoxPartials.setObjectName(_fromUtf8("checkBoxPartials"))
        self.gridLayout_5.addWidget(self.checkBoxPartials, 0, 1, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_5.addItem(spacerItem3, 0, 2, 1, 1)
        self.gridLayout_8.addWidget(self.grpOptions, 1, 0, 1, 1)
        spacerItem4 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_8.addItem(spacerItem4, 2, 0, 1, 1)
        self.groupBox_3 = QtGui.QGroupBox(self.tab_3)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_3.sizePolicy().hasHeightForWidth())
        self.groupBox_3.setSizePolicy(sizePolicy)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.gridLayout_6 = QtGui.QGridLayout(self.groupBox_3)
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.label6_3 = QtGui.QLabel(self.groupBox_3)
        self.label6_3.setMinimumSize(QtCore.QSize(80, 0))
        self.label6_3.setObjectName(_fromUtf8("label6_3"))
        self.gridLayout_6.addWidget(self.label6_3, 0, 0, 1, 1)
        self.txtMapFontsetPath = QtGui.QLineEdit(self.groupBox_3)
        self.txtMapFontsetPath.setText(_fromUtf8(""))
        self.txtMapFontsetPath.setObjectName(_fromUtf8("txtMapFontsetPath"))
        self.gridLayout_6.addWidget(self.txtMapFontsetPath, 0, 1, 1, 1)
        self.checkCreateFontFile = QtGui.QCheckBox(self.groupBox_3)
        self.checkCreateFontFile.setObjectName(_fromUtf8("checkCreateFontFile"))
        self.gridLayout_6.addWidget(self.checkCreateFontFile, 1, 0, 1, 2)
        self.gridLayout_8.addWidget(self.groupBox_3, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_3, _fromUtf8(""))
        self.gridLayout.addWidget(self.tabWidget, 1, 0, 1, 1)
        self.label.setBuddy(self.txtMapFilePath)
        self.label1.setBuddy(self.txtMapName)
        self.label5.setBuddy(self.cmbMapImageType)
        self.label2.setBuddy(self.txtMapWidth)
        self.label3.setBuddy(self.txtMapHeight)
        self.label4.setBuddy(self.cmbMapUnits)
        self.label6_2.setBuddy(self.txtMapServerUrl)
        self.label6.setBuddy(self.txtMapServerUrl)
        self.label6_5.setBuddy(self.txtMapServerUrl)
        self.label6_4.setBuddy(self.txtMapServerUrl)
        self.label6_7.setBuddy(self.txtMapServerUrl)
        self.label6_6.setBuddy(self.txtMapServerUrl)
        self.label6_3.setBuddy(self.txtMapServerUrl)

        self.retranslateUi(MapfileExportDlg)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), MapfileExportDlg.reject)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), MapfileExportDlg.accept)
        QtCore.QObject.connect(self.checkGenerateTmpl, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.templateTable.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(MapfileExportDlg)
        MapfileExportDlg.setTabOrder(self.txtMapName, self.cmbMapImageType)
        MapfileExportDlg.setTabOrder(self.cmbMapImageType, self.txtMapWidth)
        MapfileExportDlg.setTabOrder(self.txtMapWidth, self.txtMapHeight)
        MapfileExportDlg.setTabOrder(self.txtMapHeight, self.cmbMapUnits)
        MapfileExportDlg.setTabOrder(self.cmbMapUnits, self.txtMapShapePath)
        MapfileExportDlg.setTabOrder(self.txtMapShapePath, self.txtMapServerUrl)
        MapfileExportDlg.setTabOrder(self.txtMapServerUrl, self.buttonBox)

    def retranslateUi(self, MapfileExportDlg):
        MapfileExportDlg.setWindowTitle(QtGui.QApplication.translate("MapfileExportDlg", "RT MapServer Exporter - Save project to MapFile", None, QtGui.QApplication.UnicodeUTF8))
        self.btnChooseFile.setText(QtGui.QApplication.translate("MapfileExportDlg", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.txtMapFilePath.setToolTip(QtGui.QApplication.translate("MapfileExportDlg", "Name for the map file to be created from the QGIS project file", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MapfileExportDlg", "Map file", None, QtGui.QApplication.UnicodeUTF8))
        self.grpMap.setTitle(QtGui.QApplication.translate("MapfileExportDlg", "Map", None, QtGui.QApplication.UnicodeUTF8))
        self.label1.setText(QtGui.QApplication.translate("MapfileExportDlg", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.label5.setText(QtGui.QApplication.translate("MapfileExportDlg", "Image type", None, QtGui.QApplication.UnicodeUTF8))
        self.label2.setText(QtGui.QApplication.translate("MapfileExportDlg", "Width", None, QtGui.QApplication.UnicodeUTF8))
        self.label3.setText(QtGui.QApplication.translate("MapfileExportDlg", "Height", None, QtGui.QApplication.UnicodeUTF8))
        self.label4.setText(QtGui.QApplication.translate("MapfileExportDlg", "Units", None, QtGui.QApplication.UnicodeUTF8))
        self.label6_2.setText(QtGui.QApplication.translate("MapfileExportDlg", "Shape path", None, QtGui.QApplication.UnicodeUTF8))
        self.txtMapShapePath.setToolTip(QtGui.QApplication.translate("MapfileExportDlg", "Path to the folder where shapefiles are stored.", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("MapfileExportDlg", "Web", None, QtGui.QApplication.UnicodeUTF8))
        self.label6.setText(QtGui.QApplication.translate("MapfileExportDlg", "Online resource URL", None, QtGui.QApplication.UnicodeUTF8))
        self.txtMapServerUrl.setToolTip(QtGui.QApplication.translate("MapfileExportDlg", "The URL to the mapserver executable.\n"
"\n"
"For example: \n"
"http://my.host.com/cgi-bin/mapserv.exe", None, QtGui.QApplication.UnicodeUTF8))
        self.label6_5.setText(QtGui.QApplication.translate("MapfileExportDlg", "Image path", None, QtGui.QApplication.UnicodeUTF8))
        self.txtWebImagePath.setToolTip(QtGui.QApplication.translate("MapfileExportDlg", "Path to the temporary directory for writing temporary files and images. Must be writable by the user the web server is running as. Must end with a / or depending on your platform.", None, QtGui.QApplication.UnicodeUTF8))
        self.label6_4.setText(QtGui.QApplication.translate("MapfileExportDlg", "Temporary path", None, QtGui.QApplication.UnicodeUTF8))
        self.label6_7.setText(QtGui.QApplication.translate("MapfileExportDlg", "External graphic regexp", None, QtGui.QApplication.UnicodeUTF8))
        self.label6_6.setText(QtGui.QApplication.translate("MapfileExportDlg", "Image URL", None, QtGui.QApplication.UnicodeUTF8))
        self.txtWebImageUrl.setToolTip(QtGui.QApplication.translate("MapfileExportDlg", "Base URL for \"Image path\".\n"
"This is the URL that will take the web browser to \"Image path\" to get the images.", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("MapfileExportDlg", "General", None, QtGui.QApplication.UnicodeUTF8))
        self.checkTmplFromFile.setToolTip(QtGui.QApplication.translate("MapfileExportDlg", "Forces labels on, regardless of collisions. Available only for cached labels.", None, QtGui.QApplication.UnicodeUTF8))
        self.checkTmplFromFile.setText(QtGui.QApplication.translate("MapfileExportDlg", "Template from file", None, QtGui.QApplication.UnicodeUTF8))
        self.txtTemplatePath.setToolTip(QtGui.QApplication.translate("MapfileExportDlg", "Name for the map file to be created from the QGIS project file", None, QtGui.QApplication.UnicodeUTF8))
        self.btnChooseTemplate.setText(QtGui.QApplication.translate("MapfileExportDlg", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.checkGenerateTmpl.setToolTip(QtGui.QApplication.translate("MapfileExportDlg", "Forces labels on, regardless of collisions. Available only for cached labels.", None, QtGui.QApplication.UnicodeUTF8))
        self.checkGenerateTmpl.setText(QtGui.QApplication.translate("MapfileExportDlg", "Autogenerate template for layers", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("MapfileExportDlg", "Header", None, QtGui.QApplication.UnicodeUTF8))
        self.txtTmplHeaderPath.setToolTip(QtGui.QApplication.translate("MapfileExportDlg", "Name for the map file to be created from the QGIS project file", None, QtGui.QApplication.UnicodeUTF8))
        self.btnChooseTmplHeader.setText(QtGui.QApplication.translate("MapfileExportDlg", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("MapfileExportDlg", "Footer", None, QtGui.QApplication.UnicodeUTF8))
        self.txtTmplFooterPath.setToolTip(QtGui.QApplication.translate("MapfileExportDlg", "Name for the map file to be created from the QGIS project file", None, QtGui.QApplication.UnicodeUTF8))
        self.btnChooseTmplFooter.setText(QtGui.QApplication.translate("MapfileExportDlg", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QtGui.QApplication.translate("MapfileExportDlg", "Template", None, QtGui.QApplication.UnicodeUTF8))
        self.grpOptions.setTitle(QtGui.QApplication.translate("MapfileExportDlg", "Label options", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxForce.setToolTip(QtGui.QApplication.translate("MapfileExportDlg", "Forces labels on, regardless of collisions. Available only for cached labels.", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxForce.setText(QtGui.QApplication.translate("MapfileExportDlg", "Force", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxPartials.setToolTip(QtGui.QApplication.translate("MapfileExportDlg", "Can text run off the edge of the map?", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxPartials.setText(QtGui.QApplication.translate("MapfileExportDlg", "Partials", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setTitle(QtGui.QApplication.translate("MapfileExportDlg", "Fontset", None, QtGui.QApplication.UnicodeUTF8))
        self.label6_3.setText(QtGui.QApplication.translate("MapfileExportDlg", "Path", None, QtGui.QApplication.UnicodeUTF8))
        self.txtMapFontsetPath.setToolTip(QtGui.QApplication.translate("MapfileExportDlg", "path", None, QtGui.QApplication.UnicodeUTF8))
        self.checkCreateFontFile.setToolTip(QtGui.QApplication.translate("MapfileExportDlg", "Forces labels on, regardless of collisions. Available only for cached labels.", None, QtGui.QApplication.UnicodeUTF8))
        self.checkCreateFontFile.setText(QtGui.QApplication.translate("MapfileExportDlg", "Generate used fonts file", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QtGui.QApplication.translate("MapfileExportDlg", "Advanced", None, QtGui.QApplication.UnicodeUTF8))

