# ![icon](handyview/icon.png) HandyView

[English](README.md) **|** [简体中文](README_CN.md) &emsp; [GitHub](https://github.com/xinntao/HandyView) **|** [Gitee码云](https://gitee.com/xinntao/HandyView)

*Handy Series*:

<img src="https://github.com/xinntao/HandyView/blob/master/handyview/icon.png" alt="HandyView Icon" width="40" height="40"> [HandyView](https://github.com/xinntao/HandyView) &emsp; <img src="https://github.com/xinntao/HandyFigure/blob/master/icon.png" alt="HandyFigure Icon" width="40" height="40"> [HandyFigure](https://github.com/xinntao/HandyFigure) &emsp; <img src="https://github.com/xinntao/HandyCrawler/blob/master/icon.png" alt="HandyCrawler Icon" width="40" height="40"> [HandyCrawler](https://github.com/xinntao/HandyCrawler)
&emsp; <img src="https://github.com/xinntao/HandyWriting/blob/master/icon.png" alt="HandyWriting Icon" width="40" height="40"> [HandyWriting](https://github.com/xinntao/HandyWriting)

---

HandyView is a handy image viewer based on PyQt5. It provided convenient ways for viewing and comparing.

## :sparkles: Features

- Switch among images **with fixed zoom ration**, which is useful when comparing image details. (Unfortunately, I cannot find such a image viewer and this is the initial motivation to write HandyView).
- Show basic image information, for example, image path, shape, size, color type, zoom ration, etc.
- Show the position and color in the current mouse cursor.

### Current screenshot

[To be updated]

<p align="center">
  <img src="assets/screenshot.png">
</p>

## Usage

I have now tested it on Windows. It should also work on Ubuntu (but may with some modifications).

### Windows

#### Dependencies

- Anaconda (Python >= 3.5)

1. Clone repo

    ```bash
    git clone https://github.com/xinntao/HandyView.git
    ```

1. Install dependent packages

    ```bash
    cd HandyView
    pip install -r requirements.txt
    ```

In the command line, run:

> python handyview/handyview.py [image_path]

#### Compile to executable program

Use `pyinstaller` to compile to executable program, so that you can **double-click the image to open** the HandyView.

1. > pyinstaller -D handyview/handyview.py -i icon.ico --windowed
1. You will see a `dist` folder containing the outputs (dll, exe, etc)
1. Copy the `handyview/icons` folder and the `handyview/icon.png` image to the `dist` folder
1. Choose the `dist/handyview/handyview.exe` as the default image viewer.

### Ubuntu

I used Ubuntu in the previous versions. Now I switch to Windows (with wsl) for development.
So this is not tested on Ubuntu and may be out-of-date.

1. Clone this repo `git clone git@github.com:xinntao/HandyView.git`
1. How to double click to open an image
    1. Modify the HandyView.desktop file - *Exec & Icon*
    1. Copy the .desktop file to `/usr/share/applications`
1. How to change the default image viewer
    1. Right click an image
    1. Go to `Properties` -> `Open With`
    1. Choose *HandyView*

## TODO list

### Compare operations

- [ ] Given two directories, it can compare the corresponding images.

### Editing operation

- [ ] Simple image edit: crop, resize, color convertion, etc.
- [ ] Draw rectangular and enlarged this area.
- [ ] Make gif easily.

## Reference

- [Qt5 doc](https://doc.qt.io/qt-5/)
- [PyQt5 doc](https://doc.qt.io/qtforpython/api.html)
- [Key name](https://doc.qt.io/archives/qtjambi-4.5.2_01/com/trolltech/qt/core/Qt.Key.html)

## Acknowledgement

### Icons

I have used the icons from [www.flaticon.com](www.flaticon.com) The following are the source links.

- [Open icon](https://www.flaticon.com/free-icon/open_3143203?term=file%20open&page=1&position=1)
- [Refresh icon](https://www.flaticon.com/free-icon/reuse_3299869?term=refresh&page=1&position=16)
- [Include icon](https://www.flaticon.com/free-icon/add_2921226)
- [Exclude icon](https://www.flaticon.com/free-icon/remove_2921203)
- [Compare icon](https://www.flaticon.com/free-icon/file-sharing_1037325?term=file%20compare&page=1&position=2)
- [History icon](https://www.flaticon.com/free-icon/timer_2921268)
