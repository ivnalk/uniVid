import sys
import os
import subprocess
from PyQt5 import QtCore

import uniVid

class ReducirThread(QtCore.QThread):
    
    signaler = QtCore.pyqtSignal(int, str)

    def __init__(self, archivo):
        QtCore.QThread.__init__(self)
        self.archivo  = videos


    def run(self):
        self.signaler.emit(1, 'Iniciando reduccion')

        salida = '%s_reducido.mp4' % self.archivo

        try:
            # Hacer ffmpg
            comando = "ffmpeg -i %s -b 500k -y %s" % (self.archivo, salida)
            self.signaler.emit(2, comando)

            process = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,universal_newlines=True,shell=True)

        except Exception as e:
            print('fallo')
            self.signaler.emit(-1, 'El proceso falló: %s' % str(e))

    def eliminarTmp(self):
        try:
            os.remove(self.tmpFile)
        except Exception as e:
            pass