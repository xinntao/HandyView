echo 'Step 1: PYINSTALL'
pyinstaller -D handyview/handyviewer.py -i icon.ico --windowed --noconfirm

echo 'Step 2: COPY FILES'
cp -r handyview/icons dist/handyviewer/
cp handyview/icon.png dist/handyviewer/
cp icon.ico dist/handyviewer/
