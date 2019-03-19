curl -o uniVid_ffmpeg.zip https://alk.mx/archivos/uniVid_ffmpeg.zip
7z x uniVid_ffmpeg.zip
mv ffmpeg/* bin/ffmpeg

sleep 2s

rm -rf uniVid_ffmpeg.zip