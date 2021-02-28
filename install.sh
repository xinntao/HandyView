pyinstaller -D handyview/handyview.py -i icon.ico --windowed --noconfirm

cp -r handyview/icons dist/handyview/
cp handyview/icon.png dist/handyview/
