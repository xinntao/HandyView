# :yum: HandyViewer

I want to **switch among images with a fixed zoomed ration** to compare image details more conveniently, especially in super-resolution (SR).

However, most existing image viewers do not have this feature. Therefore, I want to develop an image viewer called **Handy Viewer**  to meet my requirements.

This project is still under construction, advice, bug report and development are welcome :smiley:.

### Prerequisites

- Ubuntu
- Python3
- PyQt5

## How to use

1. Clone this repo `git clone git@github.com:xinntao/HandyViewer.git`
1. How to double clike to open an image
    1. modify the HandyViewer.desktop file - *Exec & Icon*
    1. copy the .desktop file to `/usr/share/applications`
1. How to change the default image viewer 
    1. Right clike an image
    1. Go to `Properties` -> `Open With`
    1. Choose *HandyViewer*

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
