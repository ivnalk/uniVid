@echo off

setlocal

call curl -o uniVid_ffmpeg.zip https://alk.mx/archivos/uniVid_ffmpeg.zip

unzip uniVid_ffmpeg.zip
move ffmpeg\win bin\ffmpeg\
move ffmpeg\linux bin\ffmpeg\