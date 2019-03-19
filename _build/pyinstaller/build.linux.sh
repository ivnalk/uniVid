# curl -o uniVid_ffmpeg.zip https://alk.mx/archivos/uniVid_ffmpeg.zip
# 7z x uniVid_ffmpeg.zip
# mv ffmpeg/* ../../uniVid/libs/ffmpeg

rm -r build/
rm -r dist/

MACHINE_TYPE=`uname -m`
if [ ${MACHINE_TYPE} == 'x86_64' ]; then
  pyinstaller linux.x64.spec
else
  pyinstaller linux.x86.spec
fi

cp -r ../../uniVid/bin/ dist/