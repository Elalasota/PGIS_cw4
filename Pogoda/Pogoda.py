# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Pogoda
                                 A QGIS plugin
 Ta wtyczka pokazuje aktualna pogode.
                              -------------------
        begin                : 2015-01-18
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Ela Lasota
        email                : elcialas@gmail.com
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QVariant, QDateTime, QPointF, QPoint
from PyQt4.QtGui import QAction, QIcon, QColor, QBrush, QImage, QFileDialog
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from Pogoda_dialog import PogodaDialog
import os.path
from qgis.core import *
from qgis.utils import iface
import urllib, json, os, sys
import time, calendar
from datetime import datetime
from sgmllib import SGMLParser
import urllib, cStringIO
from PIL import Image
from qgis.gui import QgsMapTool, QgsMapToolEmitPoint, QgsMapCanvasItem, QgsMessageBar

class Pogoda:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Pogoda_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = PogodaDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Pogodynka')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Pogoda')
        self.toolbar.setObjectName(u'Pogoda')
	
    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Pogoda', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/Pogoda/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Sprawdz pogode'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Pogodynka'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog

        sciezka=os.path.join(os.path.expanduser("~"), ".qgis2/python/plugins/Pogoda/pogoda.json")
        sciezkaWoje=os.path.join(os.path.expanduser("~"), ".qgis2/python/plugins/Pogoda/wojewodztwa/wojewodztwa.shp")
        wektor=QgsVectorLayer(sciezkaWoje, "Wojewodztwa", "ogr")
        obi=wektor.getFeatures()
        for obie in obi:
            self.dlg.lista.addItem(obie.attribute("jpt_nazwa_"))
        def zaznacz():
            for i in range(self.dlg.lista.count()):
                self.dlg.lista.setItemSelected(self.dlg.lista.item(i), True)
        self.dlg.przycisk.clicked.connect(zaznacz)
        def zapis():
            fileName = QFileDialog.getSaveFileName(self.dlg, "Save File", "/home/untitled.shp", "Formaty *.shp *.geojson *.kml (*.shp *.geojson *.kml)")
            self.dlg.linia.setText(fileName)
        self.dlg.przycisk_2.clicked.connect(zapis)
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
			plotno=iface.mapCanvas()
			plotno.clear()
			plotno.clearCache()
			sciezka=os.path.join(os.path.expanduser("~"), ".qgis2/python/plugins/Pogoda/pogoda.json")
			sciezkaWoje=os.path.join(os.path.expanduser("~"), ".qgis2/python/plugins/Pogoda/wojewodztwa/wojewodztwa.shp")
			wektor=QgsVectorLayer(sciezkaWoje, "Wojewodztwa", "ogr")
			print wektor.crs().authid()
			warstwa=QgsVectorLayer("Polygon?index=yes&crs="+wektor.crs().authid(),"Pogoda","memory")
			warstwa.startEditing()
			pola=wektor.dataProvider().fields()
			for pole in pola:
				warstwa.addAttribute(pole)
			miasta=[756135, 3080165, 3083829, 3099434, 763166, 776069, 765876, 759734, 3096472, 3094802, 3090048, 3081368, 3088171, 3102014, 769250, 3093133]
			adres="http://api.openweathermap.org/data/2.5/group?units=metric&lang=pl&APPID=7669678a4b5d0f3d5aa0205a2f0f2fe9&id="
			for miasto in miasta:
				adres=adres+str(miasto)+","
			print adres
			try:
				f=open(sciezka,'r')
			except IOError:
				f=open(sciezka, 'w+')
			tgj=f.read()
			f.close()
			try:
				gej=json.loads(tgj)
				czasP=gej['data']
			except ValueError:
				czasP=0
			print czasP, "czas pobrania"
			czasA=calendar.timegm(time.gmtime())
			roznica=czasA-czasP
			print roznica, "roznica"
			bar=iface.messageBar()
			if roznica>600:
				f=open(sciezka,'w+')
				usock = urllib.urlopen(adres)
				zrodlo = usock.read()
				usock.close()
				try:
					gj=json.loads(zrodlo)
				except ValueError:
					print "Brak danych"
				gj['data']=calendar.timegm(time.gmtime())
				f.write(json.dumps(gj,f))
				f.close()
			else:
				gj=gej
			bar.pushMessage("Dane zaladowano")
			newCrs=QgsCoordinateReferenceSystem(wektor.crs()) 
			oldCrs=QgsCoordinateReferenceSystem(4326)
			transformacja=QgsCoordinateTransform(oldCrs, newCrs)
			wektor.startEditing()
			atrybuty=["Temp", "TempMax", "TempMin", "Cisnienie", "Wilgotnosc", "PredWiatru", "KierWiatru", "Chmury"]
			for atr in atrybuty:
				if wektor.dataProvider().fieldNameIndex(atr)==-1:
					wektor.dataProvider().addAttributes([QgsField(atr, QVariant.Double)])
			if wektor.dataProvider().fieldNameIndex('DataPob')==-1:
				wektor.dataProvider().addAttributes([QgsField('DataPob', QVariant.String)])
			wektor.updateFields()
			slownik=gj['list']
			adresik="http://openweathermap.org/img/w/"
			wszystko={}
			for i in range(0, len(slownik)):
				tmp=slownik[i]['main']['temp']
				tmpmax=slownik[i]['main']['temp_max']
				tmpmin=slownik[i]['main']['temp_min']
				cisn=slownik[i]['main']['pressure']
				wilg=slownik[i]['main']['humidity']
				prw=slownik[i]['wind']['speed']
				kw=slownik[i]['wind']['deg']
				chm=slownik[i]['clouds']['all']
				czas=slownik[i]['dt']
				symbol=slownik[i]['weather'][0]['icon']
				data2=datetime.fromtimestamp(czas).strftime('%Y-%m-%d %H:%M:%S')
				wartosci=[tmp, tmpmax, tmpmin, cisn, wilg, prw, kw,chm]
				punkt=QgsPoint(slownik[i]['coord']['lon'],slownik[i]['coord']['lat'])
				punkt_nowy=transformacja.transform(punkt)
				for obiekt in wektor.getFeatures():
					if obiekt.geometry().contains(QgsGeometry.fromPoint(punkt_nowy)):
						for i in xrange(0, len(atrybuty)):
							obiekt.setAttribute(atrybuty[i], wartosci[i])
						obiekt.setAttribute('DataPob',data2)
						adres2=adresik+symbol+".png"
						plik = urllib.urlopen(adres2).read()
						img = QImage()
						img.loadFromData(plik)
						#print img.height()
						wszystko[obiekt.attribute('jpt_nazwa_')]=[symbol, punkt_nowy, img]
						#print obiekt.attribute('jpt_nazwa_')
						wektor.updateFeature(obiekt)
			wektor.commitChanges()
			rysowanie={}
			wybrane=self.dlg.lista.selectedItems()
			pytaj=""
			for wybor in wybrane:
				pytaj=pytaj+"jpt_nazwa_="+"'"+wybor.text()+"' or "
				rysowanie[wybor.text()]=wszystko[wybor.text()]
			pytaj=pytaj[:len(pytaj)-4]
			zapytanie=QgsExpression(pytaj)
			zapytanie.prepare(wektor.pendingFields())
			wojewodztwo=filter(zapytanie.evaluate, wektor.getFeatures())
			wektor.removeSelection()
			warstwa.addFeatures(wojewodztwo)
			warstwa.commitChanges()
			warstwa.removeSelection()
			QgsMapLayerRegistry.instance().addMapLayer(warstwa)
			warstwa.updateExtents()
			zasieg=warstwa.extent()
			plotno.setExtent(zasieg)
			class RysObraz(QgsMapCanvasItem):
				def __init__(self,mapCanvas):
					QgsMapCanvasItem.__init__(self,mapCanvas)
					self.canvas=mapCanvas
					self.draw=False
					self.punkt=QgsPoint(0,0)
				def setObiekt(self, obiekt):
					self.obiekt=obiekt
					self.draw=True
					self.punkt=self.obiekt[1]
				def paint(self,painter,option,widget):
					if self.draw:
						wys=self.obiekt[2].height()/2
						szer=self.obiekt[2].width()/2
						pu=self.toCanvasCoordinates(self.punkt)
						iks=pu.x()
						igrek=pu.y()
						pu.setX(iks-szer)
						pu.setY(igrek-wys)
						painter.drawImage(pu,self.obiekt[2])
						self.canvas.refresh()
			for klucz in rysowanie:
				rysunek=RysObraz(plotno)
				#print rysowanie[klucz]
				rysunek.setObiekt(rysowanie[klucz])
			sc=self.dlg.linia.displayText()
			if sc:
				zap=sc.split('.')
				format=zap[len(zap)-1]
				if format=="shp":
					zapi="ESRI Shapefile"
				elif format=="geojson":	
					zapi="GeoJSON"
				elif format=="kml":
					zapi="KML"
				else:
					zapi=""
				QgsVectorFileWriter.writeAsVectorFormat(warstwa, sc, "utf-8", warstwa.crs(), zapi)
			
			print "Zakonczono"
			
			symbol_layer = QgsSimpleMarkerSymbolLayerV2()
			myRangeList = []
			myLabel='Smierc na miejscu'
			myMin=-100
			myMax=-15
			myColour=QColor('#25437F')
			mySymbol1=QgsSymbolV2.defaultSymbol(warstwa.geometryType())
			mySymbol1.setColor(myColour)
			myRange1=QgsRendererRangeV2(myMin, myMax, mySymbol1, myLabel)
			myRangeList.append(myRange1)

			myLabel='Pizga jak szatan'
			myMin=-14.9
			myMax=0
			myColour=QColor('#4A85FF')
			mySymbol2=QgsSymbolV2.defaultSymbol(warstwa.geometryType())
			mySymbol2.setColor(myColour)
			myRange2=QgsRendererRangeV2(myMin, myMax, mySymbol2, myLabel)
			myRangeList.append(myRange2)


			myLabel='Troche wieje po lydkach'
			myMin=0.1
			myMax=7
			myColour=QColor('#9BFFE0')
			mySymbol3=QgsSymbolV2.defaultSymbol(warstwa.geometryType())
			mySymbol3.setColor(myColour)
			myRange3=QgsRendererRangeV2(myMin, myMax, mySymbol3, myLabel)
			myRangeList.append(myRange3)

			myLabel='Wiosna idzie'
			myMin=7.1
			myMax=15.0
			myColour=QColor('#B5FF99')
			mySymbol4=QgsSymbolV2.defaultSymbol(warstwa.geometryType())
			mySymbol4.setColor(myColour)
			myRange4=QgsRendererRangeV2(myMin, myMax, mySymbol4, myLabel)
			myRangeList.append(myRange4)

			myLabel='Cieplutko sie robi'
			myMin=15.1
			myMax=20
			myColour=QColor('#C3FF45')
			mySymbol5=QgsSymbolV2.defaultSymbol(warstwa.geometryType())
			mySymbol5.setColor(myColour)
			myRange5=QgsRendererRangeV2(myMin, myMax, mySymbol5, myLabel)
			myRangeList.append(myRange5)
			
			myLabel='Idealnie'
			myMin=20.1
			myMax=27
			myColour=QColor('#FBFF46')
			mySymbol6=QgsSymbolV2.defaultSymbol(warstwa.geometryType())
			mySymbol6.setColor(myColour)
			myRange6=QgsRendererRangeV2(myMin, myMax, mySymbol6, myLabel)
			myRangeList.append(myRange6)
			
			myLabel='Patelnia'
			myMin=27.1
			myMax=37
			myColour=QColor('#FF950C')
			mySymbol7=QgsSymbolV2.defaultSymbol(warstwa.geometryType())
			mySymbol7.setColor(myColour)
			myRange7=QgsRendererRangeV2(myMin, myMax, mySymbol7, myLabel)
			myRangeList.append(myRange7)
			
			myLabel='Smierc'
			myMin=37.1
			myMax=100
			myColour=QColor('#FF1700')
			mySymbol8=QgsSymbolV2.defaultSymbol(warstwa.geometryType())
			mySymbol8.setColor(myColour)
			myRange8=QgsRendererRangeV2(myMin, myMax, mySymbol8, myLabel)
			myRangeList.append(myRange8)
			
			myRenderer=QgsGraduatedSymbolRendererV2('', myRangeList)
			myRenderer.setMode(QgsGraduatedSymbolRendererV2.Custom)
			myRenderer.setClassAttribute("Temp")
			warstwa.setRendererV2(myRenderer)
			plotno.refresh()
			warstwa.updateExtents()
