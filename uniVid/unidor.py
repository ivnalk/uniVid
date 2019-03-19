import sys
import os
import subprocess
import platform

from PyQt5 import QtCore

import uniVid

class UnidorThread(QtCore.QThread):
    
    signaler = QtCore.pyqtSignal(int, str)

    def __init__(self, videos, output, app_path):
        QtCore.QThread.__init__(self)
        self.videos  = videos
        self.output  = output
        self.tmpFile = '%s/uniVid.tmp' % os.getcwd()

        ARCH = platform.architecture()

        if getattr(sys, 'frozen', False):
            bundle_dir = sys._MEIPASS
        else:
            bundle_dir = os.path.dirname(os.path.abspath(__file__))

        if ARCH == '64bit':
            P_AR = 'x64'
        else:
            P_AR = 'x86'

        if os.name == 'nt':
            P_OS = 'win'
            cmd_ffmpeg = 'ffmpeg.exe'
            cmd_ffprobe = 'ffprobe.exe'
        else:
            P_OS = 'linux'
            cmd_ffmpeg = 'ffmpeg'
            cmd_ffprobe = 'ffprobe'

        self.ffmpeg  = os.path.join( app_path, 'bin/ffmpeg/%s/%s/%s' % (P_OS, P_AR, cmd_ffmpeg) )
        self.ffprobe = os.path.join( app_path, 'bin/ffmpeg/%s/%s/%s' % (P_OS, P_AR, cmd_ffprobe) )


    def run(self):
        self.signaler.emit(1, 'Iniciando unión')

        self.output.replace('.', '')

        ext = self.output[-3:]
        if self.output[-3:] == "mp4" or self.output[:-3] == "MP4":
            # forzar lowercase de extension
            pass
        else:
            self.output += '.mp4'

        archivos      = ''
        archivosTotal = len(self.videos)

        self.eliminarTmp()

        totalFps = 0
        totalDuracion = 0

        f = open(self.tmpFile,"w+") 
        for vid in self.videos:
            tmpLine = "file '%s'\r\n" % vid
            f.write(tmpLine)

            cmdDuration = [self.ffprobe, '-i', vid, '-show_entries', 'format=duration', '-v', 'quiet', '-of', 'default=noprint_wrappers=1:nokey=1']
            cmdFrames   = [self.ffprobe, '-v', 'error', '-select_streams', 'v', '-of', 'default=noprint_wrappers=1:nokey=1', '-show_entries', 'stream=r_frame_rate', vid] 
            
            durProcess = subprocess.Popen(cmdDuration, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            durOut = durProcess.communicate()
            
            duracion = float( durOut[0].decode('utf-8').rstrip("\r\n") )
            totalDuracion += duracion

            fpsProcess = subprocess.Popen(cmdFrames, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            fpsOut = fpsProcess.communicate()
            
            cuadrosInfo = fpsOut[0].decode('utf-8')

            cuadrosOp = cuadrosInfo.split('/')
            cuadrosFps = round( int(cuadrosOp[0]) / int(cuadrosOp[1]) )

            totalFps += int( round( duracion * cuadrosFps ) )

        f.close()


        try:
            # Hacer ffmpg
            comando = "%s -f concat -safe 0 -i %s -c:v copy -c:a aac -y %s" % (self.ffmpeg, self.tmpFile, self.output)
            self.signaler.emit(2, comando)

            process = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,universal_newlines=True,shell=True)

            while True:
                line = process.stdout.readline()
                if not line:
                    break
                tmp = line.strip()
                if "time=" in tmp:
                    outDuration = tmp.split("time=")
                    outDuration = outDuration[1].split("time=")
                    outDuration = outDuration[0].split(" ")

                    avanceDuracion   = self.get_sec(outDuration[0])
                    porcentajeAvance = round( (avanceDuracion * 100) / totalDuracion )

                    self.signaler.emit(88, '%s' % porcentajeAvance)

            self.eliminarTmp()
            self.signaler.emit(99, 'Terminado')

        except Exception as e:
            print('fallo', str(e))
            self.signaler.emit(-1, 'El proceso falló: %s' % str(e))

    def eliminarTmp(self):
        try:
            os.remove(self.tmpFile)
        except Exception as e:
            pass

    def get_sec(self, time_str):
        h, m, s = time_str.split(':')
        return int(h) * 3600 + int(m) * 60 + float(s)