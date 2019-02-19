@echo off

setlocal

call curl -o uniVid_ffmpeg.zip https://alk.mx/archivos/uniVid_ffmpeg.zip

unzip uniVid_ffmpeg.zip
move ffmpeg/* ../../uniVid/libs/ffmpeg/

:: falta hacer el build real xD