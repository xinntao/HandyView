#!/bin/sh
# Create a folder (named dmg) to prepare our DMG in (if it doesn't already exist).
mkdir -p dist/dmg
# Empty the dmg folder.
rm -r dist/dmg/*
# Copy the app bundle to the dmg folder.
cp -r "dist/handyviewer.app" dist/dmg
# If the DMG already exists, delete it.
test -f "dist/handyvichewer.dmg" && rm "dist/handyviewer.dmg"


create-dmg \
  --volname "handyviewer" \
  --volicon "icon.icns" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --icon "handyviewer.app" 200 190 \
  --hide-extension "handyviewer.app" \
  --app-drop-link 600 185 \
  "dist/handyviewer.dmg" \
  "dist/dmg/"