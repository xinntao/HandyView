echo 'Step 1: PYINSTALL'
pyinstaller -D handyview/handyviewer.py -i icon.ico --windowed --noconfirm

echo 'Step 2: COPY FILES'
cp -r icons dist/handyviewer/
cp icon.png dist/handyviewer/
cp icon.ico dist/handyviewer/
