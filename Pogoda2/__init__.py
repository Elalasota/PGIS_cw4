# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Pogoda
                                 A QGIS plugin
 Wtyczka z prognoza pogody
                             -------------------
        begin                : 2015-01-07
        copyright            : (C) 2015 by Ela Lasota
        email                : elcialas@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Pogoda class from file Pogoda.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .Pogoda2 import Pogoda
    return Pogoda(iface)
