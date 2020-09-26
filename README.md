# :yum: HandyView

## Reference

- [Qt5 doc](https://doc.qt.io/qt-5/)
- [PyQt5 doc](https://doc.qt.io/qtforpython/api.html)

- [Key name](https://doc.qt.io/archives/qtjambi-4.5.2_01/com/trolltech/qt/core/Qt.Key.html)

- menubar
- toolbar


- icon
  - open: https://www.flaticon.com/free-icon/open_3143203?term=file%20open&page=1&position=1
  - refresh: https://www.flaticon.com/free-icon/reuse_3299869?term=refresh&page=1&position=16
  - compare: https://www.flaticon.com/free-icon/file-sharing_1037325?term=file%20compare&page=1&position=2
  - file history: https://www.flaticon.com/free-icon/file_1570376?term=file%20history&page=1&position=70

I want to **switch among images with a fixed zoomed ration** to compare image details more conveniently, especially in super-resolution (SR).

However, most existing image viewers do not have this feature. Therefore, I want to develop an image viewer called **Handy Viewer**  to meet my requirements.

This project is still under construction, advice, bug report and development are welcome :smiley:.

### Current screenshot
<p align="center">
  <img src="https://c1.staticflickr.com/1/975/40897859985_9fa4f67558_b.jpg">
</p>

### Prerequisites

- Ubuntu
- Python3
- PyQt5

## How to use

1. Clone this repo `git clone git@github.com:xinntao/HandyViewer.git`
1. How to double clike to open an image
    1. modify the HandyView.desktop file - *Exec & Icon*
    1. copy the .desktop file to `/usr/share/applications`
1. How to change the default image viewer
    1. Right clike an image
    1. Go to `Properties` -> `Open With`
    1. Choose *HandyView*

## Features

### View
- [x] When swith between different images, the zoom scale and postion can be maintained.
- [x] Show some info, e.g., image path, image width & height, color type(RGB, RGBA, L and etc), zoom ration.
- [x] Show cursor position (in image pixel, ignoring zoom ration) [for draw rectangular, crop later]
- [ ] Given two directories, it can compare the corresponding images (image names in the two directories can be the same.)

### Edit
- [ ] Simple image edit: crop, resize, rgb_ycbcr convertion and etc.
- [ ] Draw rectangular and enlarged this area.
- [ ] make gif easily.
