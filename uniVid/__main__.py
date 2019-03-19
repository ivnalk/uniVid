#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#######################################################################
#
# uniVid - media joiner
#
# copyright © 2019 Ivan Abacal
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#######################################################################

import logging
import logging.handlers
import os
import shutil
import signal
import sys
import traceback
from functools import partial

from uniVid.unidor import UnidorThread
from uniVid.reducir import ReducirThread

from typing import Callable, Optional

from PyQt5 import uic 

from PyQt5.QtCore import (pyqtSlot, QCommandLineOption, QCommandLineParser, QDir, QFileInfo, QProcess,
                          QProcessEnvironment, QSettings, QSize, QStandardPaths, QTimerEvent, Qt)
from PyQt5.QtGui import (QIcon, QCloseEvent, QContextMenuEvent, QDragEnterEvent, QDropEvent, QGuiApplication, QMouseEvent,
                         QResizeEvent, QSurfaceFormat, qt_set_sequence_auto_mnemonic)
from PyQt5.QtWidgets import qApp, QMainWindow, QMessageBox, QSizePolicy, QDesktopWidget, QFileDialog

import uniVid
from uniVid.libs.singleapplication import SingleApplication


if sys.platform == 'win32':
    # from vidcutter.libs.taskbarprogress import TaskbarProgress
    # noinspection PyUnresolvedReferences
    from PyQt5.QtWinExtras import QWinTaskbarButton

signal.signal(signal.SIGINT, signal.SIG_DFL)
signal.signal(signal.SIGTERM, signal.SIG_DFL)

if hasattr(sys, 'frozen'):
    basis = sys.executable
else:
    basis = sys.argv[0]
app_path = os.path.split(basis)[0]

if getattr(sys, 'frozen', False):
    bundle_dir = sys._MEIPASS
else:
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

pathGUI = os.path.join( bundle_dir, 'ui/forms/wndMain.ui' )

ventana = uic.loadUiType(pathGUI)[0]

class wndMain(QMainWindow, ventana):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.setWindowFlags(
            Qt.Window |
            Qt.CustomizeWindowHint |
            Qt.WindowTitleHint |
            Qt.WindowCloseButtonHint |
            Qt.WindowStaysOnTopHint |
            Qt.WindowMinimizeButtonHint |
            Qt.WindowSystemMenuHint
        )

        # Centrar ventana
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        # Defaults
        self.threads     = []
        self.uniendo     = 0
        self.qtyArchivos = 0
        self.qtyArchivosReducir = 0

        self.btnArchivoReducirSel.clicked.connect(self.on_seleccionarReducir)
        self.btnReducir.clicked.connect(self.on_reducir)

        self.btnLimpiar.clicked.connect(self.on_limpiarLista)
        self.btnUnir.clicked.connect(self.on_unirArchivos)

        # self.btnQuitar.setEnabled(False)
        self.btnQuitar.clicked.connect(self.on_quitarArchivo)

        self.btnAgregar.clicked.connect( partial(self.on_agregarArchivo, None) )

        self.btnSubir.clicked.connect( partial(self.on_moverItem, 'arriba') )
        self.btnBajar.clicked.connect( partial(self.on_moverItem, 'abajo') )


    def on_seleccionarReducir(self):
        options                = QFileDialog.Options()
        archivoSeleccionado, _ = QFileDialog.getOpenFileName(self, 'Selecciona un archivo de video', '', 'Archivos MP4 (*.mp4)')
        
        if archivoSeleccionado:
            self.txtArchivoReducir.setText(archivoSeleccionado)
            self.qtyArchivosReducir = 1

    def on_reducir(self):
        if self.reducir == 0 and self.qtyArchivosReducir == 1:
            self.init_reduce()
        else:
            self.mensaje('critical', 'Vaya, esto no se puede reducir.')

    def init_reduce(self):
        self.reduce = ReducirThread(archivo)
        self.reduce.signaler.connect(self.on_ReduciendoArchivo)
        self.threads.append(self.reduce)
        self.reduce.start()

        self.qtyArchivosReducir = 0
        pass

    def mensaje(self, tipo, contenido):
        msg = QMessageBox()

        if tipo == 'warning':
            msg.setIcon(QMessageBox.Warning)
        elif tipo == 'information':
            msg.setIcon(QMessageBox.Information)
        elif tipo == 'critical':
            msg.setIcon(QMessageBox.Critical)
        else:
            msg.setIcon(QMessageBox.Question)

        msg.setText(contenido)
        msg.setWindowTitle("Error")
        showMsg = msg.exec_()

    def on_moverItem(self, direccion ):
        currentRow = self.lstArchivos.currentRow()

        if direccion == 'arriba':
            newIndex = currentRow - 1
        else:
            newIndex = currentRow + 1

        currentItem = self.lstArchivos.takeItem(currentRow)
        self.lstArchivos.insertItem(newIndex, currentItem)
        self.lstArchivos.setCurrentRow(newIndex)

    def mostrarElementos(self, accion):
        self.btnQuitar.setEnabled(accion)
        self.btnSubir.setEnabled(accion)
        self.btnBajar.setEnabled(accion)
        self.btnUnir.setEnabled(accion)
        self.btnLimpiar.setEnabled(accion)

    def on_quitarArchivo(self):
        if self.qtyArchivos == 1:
            self.mostrarElementos(False)

        if self.uniendo == 0 and self.qtyArchivos > 0:
            
            archivoSeleccionado = self.lstArchivos.currentRow()
            if archivoSeleccionado >= 0:
                self.lstArchivos.takeItem(archivoSeleccionado)

                if self.qtyArchivos > 1:
                    self.qtyArchivos = self.qtyArchivos - 1
                else:
                    self.qtyArchivos = 0
            else:
                self.mensaje('information', 'Selecciona un archivo para poder quitarlo.')
        else:
            self.mensaje('critical', 'No hay nada para quitar.')

    def agregarItem(self, item):
        self.lstArchivos.addItem(item)
        self.qtyArchivos += 1

        if self.qtyArchivos > 1:
            self.mostrarElementos(True)

    def on_agregarArchivo(self, filename=None):
        if filename is None :
            options                = QFileDialog.Options()
            archivoSeleccionado, _ = QFileDialog.getOpenFileNames(self, 'Selecciona un archivo de video', '', 'Archivos MP4 (*.mp4)')
            
            for archivo in archivoSeleccionado:
                self.agregarItem(archivo)

        else:
            self.agregarItem(filename)

    def on_limpiarLista(self):
        if self.uniendo == 0:
            self.lstArchivos.clear()
            self.loader.setValue(0)
            self.loader.setFormat('')
            self.loader.setTextVisible(False)
            self.mostrarElementos(False)


    def on_unirArchivos(self):
        if self.uniendo == 0 and self.qtyArchivos >= 2:
            self.deshabilitarElementos()
            self.init_loader()
            self.init_union()
        else:
            self.mensaje('critical', 'Vaya, esto no se puede unir.')


    def init_union(self):
        options       = QFileDialog.Options()
        fileOutput, _ = QFileDialog.getSaveFileName(self,
            'Guardar archivo',
            "union.mp4",
            "Archivo MP4 (*.mp4)",
            options=options)
        if fileOutput:
            self.uniendo = 1
            self.loader.setFormat("%p%") 
            self.loader.setTextVisible(True)

            # Listar archivos
            archivos =  [str(self.lstArchivos.item(i).text()) for i in range(self.lstArchivos.count())]

            self.union = UnidorThread(archivos, fileOutput, app_path)
            self.union.signaler.connect(self.on_UniendoArchivos)
            self.threads.append(self.union)
            self.union.start()
        else:
            self.habilitarElementos()

    pyqtSlot(int, str)
    def on_UniendoArchivos(self, num, txt):

        if num == -1:
            self.habilitarElementos()
            self.uniendo = 0
            self.mensaje('critical', 'Algo impide la unión:\n\n ' + str(e))

        elif num == 1:
            # Iniciando union
            print('inicio', txt)
        elif num == 2:
            # Comando preparado
            print('Comando: ', txt)
            pass
        elif num == 88:
            # Actualizar avance
            val = int(txt)
            
            if val >= 100:
                val = 100
                self.loader.setFormat('Procesando... espera')

            self.loader.setValue(val)
            
        elif num == 99:
            # Terminado
            print('end', txt)
            self.uniendo = 0
            self.loader.setFormat('Terminado')
            self.loader.setValue(100)
            self.habilitarElementos()

            LOADER_COMPLETADO = """
                QProgressBar{
                    border: 1px solid #223168;
                    border-radius: 2px;
                    text-align: center;
                    color: #171d22;
                    text-shadow: 0px 0px 10px black;
                }

                QProgressBar::chunk {
                    background-color: #333f6d;
                    width: 10px;
                    margin: 0px;
                }
            """

            self.loader.setStyleSheet(LOADER_COMPLETADO)


    def init_loader(self):
        LOADER_INIT = """
            
            }
        """
        self.loader.setValue(0)
        self.loader.setTextVisible(True)
        self.loader.setStyleSheet(LOADER_INIT)


    def fini_loader(self):
        self.loader.setValue(0)
        self.loader.setTextVisible(False)

    def deshabilitarElementos(self):
        self.lstArchivos.setEnabled(False)
        self.btnSubir.setEnabled(False)
        self.btnBajar.setEnabled(False)

        self.btnQuitar.setEnabled(False)
        self.btnAgregar.setEnabled(False)

        self.btnUnir.setEnabled(False)
        self.btnLimpiar.setEnabled(False)

    def habilitarElementos(self):
        self.lstArchivos.setEnabled(True)
        self.btnSubir.setEnabled(True)
        self.btnBajar.setEnabled(True)

        self.btnQuitar.setEnabled(True)
        self.btnAgregar.setEnabled(True)

        self.btnUnir.setEnabled(True)
        self.btnLimpiar.setEnabled(True)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        error = 0
        try:
            files = [u.toLocalFile() for u in event.mimeData().urls()]
            for f in files:
                if QFileInfo(f).suffix() == 'mp4':
                    self.on_agregarArchivo(f)
                else:
                    error += 1
        except Exception as e:
            self.mensaje('critical', 'No se pudo agregar la información: ' + str(e))

        if error > 0:
            self.mensaje('information', 'Uno o más archivos no se agregaron por que no son MP4, verifica e intentalo de nuevo.');

    def closeEvent(self, event: QCloseEvent) -> Optional[Callable]:
        event.accept()
        try:
            if self.uniendo == 1:
                preguntaSalir = QMessageBox.question(self,
                    uniVid.__appname__,
                    'Si cierras el programa ahora, no se uniran los videos. \n\n ¿Quieres cerrarlo ahora?',
                    QMessageBox.No | QMessageBox.Yes, QMessageBox.No)
                
                if preguntaSalir == QMessageBox.Yes:
                    qApp.exit(0)
                else:
                    event.ignore()
                    return
        except AttributeError:
            logging.exception('warning dialogs on app exit exception', exc_info=True)


    def on_seleccionadoItem(self):
        pass

        
def main():
    app = SingleApplication(uniVid.__appid__, sys.argv)
    app.setApplicationName(uniVid.__appname__)
    app.setApplicationVersion(uniVid.__version__)
    app.setDesktopFileName(uniVid.__desktopid__)
    app.setOrganizationDomain(uniVid.__domain__)
    app.setQuitOnLastWindowClosed(True)

    win = wndMain()
    app.setActivationWindow(win)
    win.show()
    exit_code = app.exec_()
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()