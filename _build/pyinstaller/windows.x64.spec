#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
# noinspection PyUnresolvedReferences
import PyQt5
import sys
sys.path.insert(0, "../..")

import uniVid

block_cipher = None
 
a = Analysis(['../../uniVid/__main__.py'],
             pathex=[
                 os.path.join(sys.modules['PyQt5'].__path__[0], 'Qt', 'bin'),
                 '../..'
             ],
             binaries=[],
             datas=[
                 ('../../uniVid/__init__.py', '.'),
                 ('../../LICENSE', '.'),
                 ('../../uniVid/ui/forms/*', 'ui/forms/'),
                 ('../../uniVid/ui/images/*', 'ui/images/'),
                 ('../../uniVid/ui/recursos.qrc', 'ui/recursos.qrc'),
                 ('../../uniVid/ui/recursos.qrc', 'ui/recursos.qrc'),
                 ('../../uniVid/libs/ffmpeg/linux/x64/*', 'libs/ffmpeg/linux/x64/'),
                 ('../../uniVid/libs/singleapplication.py', 'libs/singleapplication.py'),
                 ('../../recursos_rc.py', '.')
             ],
             hiddenimports=['PyQt5.sip'],
             runtime_hooks=[],
             excludes=['numpy'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=uniVid.__appname__,
          debug=False,
          strip=False,
          upx=False,
          console=False )