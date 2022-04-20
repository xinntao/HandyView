# ![icon](icon.png) HandyView

[English](README.md) **|** [简体中文](README_CN.md) &emsp; [GitHub](https://github.com/xinntao/HandyView) **|** [Gitee码云](https://gitee.com/xinntao/HandyView)

```Handy``` *Series*:

<img src="https://gitee.com/xinntao/HandyView/raw/master/icon.png" alt="HandyView Icon" width="36" height="36"> [HandyView](https://gitee.com/xinntao/HandyView) &emsp; <img src="https://gitee.com/xinntao/HandyFigure/raw/master/icon.png" alt="HandyFigure Icon" width="36" height="36"> [HandyFigure](https://gitee.com/xinntao/HandyFigure) &emsp; <img src="https://gitee.com/xinntao/HandyCrawler/raw/master/icon.png" alt="HandyCrawler Icon" width="36" height="36"> [HandyCrawler](https://gitee.com/xinntao/HandyCrawler)
&emsp; <img src="https://gitee.com/xinntao/HandyWriting/raw/master/icon.png" alt="HandyWriting Icon" width="36" height="36"> [HandyWriting](https://gitee.com/xinntao/HandyWriting)

---

HandyView 是一款基于 PyQt5 开发的方便的图像查看和比对工具.

## :sparkles: 特性

- **固定放大比率**下, 图像切换对比. 能够看出不同方法(不同参数)下复原图像的细微差异
- 显示图像基本信息: 长宽, 尺寸大小; 特别是**鼠标所在位置**的坐标和RGB颜色
- 更丰富实用的**对比模式**. 比如:
    - 我们做实验, 往往会把得到的验证集结果放在**两个文件夹**里面, 比如 Exp_results_1 和 Exp_results_2, 这两个文件夹里面的图像往往是对应的. 那么, 我们希望能够方便快捷地对比这两个文件夹里图像的质量
    - 除了上面提到的**切换图像**来*动态地*对比, 我们也希望能够**双栏/多栏***肩并肩地*对比
- 更加便捷地筛选需要对比的图像. 在实际实验中, 往往会把很多结果放在同一个文件夹里面. 这些图像仅仅是后缀名称不同. 那么我们希望根据后缀的字符来**包含或者剔除**一些对比图像
- 能够在图中画框, 方便地知道所画框的**起始位置**和长宽信息

## :eyes: 展示

- HandyView截图

<p align="center">
  <img src="assets/screenshot.png">
</p>

- **固定放大比率**下, 图像切换对比

<p align="center">
  <img src="assets/hv_switch.gif" height="400">
</p>

- 多视图比较, 双栏、三栏*肩并肩*比较

<p align="center">
  <img src="assets/hv_cmp.gif" height="400">
</p>

- 当移动鼠标, 右侧会显示当前鼠标所在坐标及像素颜色值

<p align="center">
  <img src="assets/hv_mousemove.gif" height="400">
</p>

- 拖动鼠标画框时, 右边会显示框的起始位置和长宽信息

<p align="center">
  <img src="assets/hv_rect.gif" height="400">
</p>

## :wrench: 使用

HandyView 目前实在Windows上测试的. 应该也可以在 Ubuntu 上使用, 可能需要做些改动.

### <img src="https://upload.wikimedia.org/wikipedia/commons/8/8d/Windows_darkblue_2012.svg" alt="Windows" height="28">

#### Option 1: Pre-compiled executable zip file

I have zipped an exe zip file with pyinstaller in the release page ([Github](https://github.com/xinntao/HandyView/releases) | [Gitee](https://gitee.com/xinntao/HandyView/releases)). You can first have a try on it.

1. Unzip the file
2. Set HandyView as the default image viewer, so that you can **double-click the image to open** HandyView.

#### Option 2: Python environment

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

> python handyview/handyviewer.py [image_path]

#### Option 3: Python environment + Compile to executable program

Use `pyinstaller` to compile to executable program, so that you can **double-click the image to open** the HandyView.

1. > pyinstaller -D handyview/handyview.py -i icon.ico --windowed
1. You will see a `dist` folder containing the outputs (dll, exe, etc)
1. Copy necessary files to the `dist` folder
    > cp -r icons dist/handyviewer/ <br>
    > cp icon.png dist/handyviewer/ <br>
    > cp icon.ico dist/handyviewer/ <br>
1. Choose the `dist/handyview/handyviewer.exe` as the default image viewer.

### <img src="https://upload.wikimedia.org/wikipedia/commons/3/3a/Logo-ubuntu_no%28r%29-black_orange-hex.svg" alt="Ubuntu" height="24">

I used the early version of HandyView on Ubuntu. The current version is not tested on Ubuntu and may be out-of-date.

1. Clone this repo `git clone git@github.com:xinntao/HandyView.git`
1. How to double click to open an image
    1. Modify the HandyView.desktop file - *Exec & Icon*
    1. Copy the .desktop file to `/usr/share/applications`
1. How to change the default image viewer
    1. Right click an image
    1. Go to `Properties` -> `Open With`
    1. Choose *HandyView*

## :book: 文档 (还在路上...)

基本的操作可以通过 工具栏的 *Help* 按钮来查看

## :hourglass_flowing_sand: TODO list

- [ ] preview mode
- [ ] show zoom info for each folder (store in database)
- [ ] drag together in the multi-view comparison mode
### Editing operation

- [ ] Simple image edit: crop, resize, color conversion, etc
- [ ] Draw rectangular and enlarged the area
- [ ] Make GIF easily

## :books: References

- [Qt5 doc](https://doc.qt.io/qt-5/)
- [PyQt5 doc](https://doc.qt.io/qtforpython/api.html)
- [Qt Key](https://doc.qt.io/archives/qtjambi-4.5.2_01/com/trolltech/qt/core/Qt.Key.html)

## :scroll: 许可和致谢

本项目使用 [MIT license](./LICENSE).

### 图标

I have used the icons from [flaticon](www.flaticon.com). The following are the source links.

| Icon | Link | Icon | Link | Icon |Link|
| :--- | :---:        |     :---      | :---: | :---        |     :---:      |
| <img src="icons/open.png" height="32" alt="Open">  | [Open](https://www.flaticon.com/free-icon/open_3143203?term=file%20open&page=1&position=1) | <img src="icons/history.png" height="32" alt="History">|[History](https://www.flaticon.com/free-icon/timer_2921268) | <img src="icons/refresh.png" height="32" alt="Refresh"> |[Refresh](https://www.flaticon.com/free-icon/reuse_3299869?term=refresh&page=1&position=16) |
| <img src="icons/index.png" height="32" alt="Index">  | [Index](https://www.flaticon.com/free-icon/index_2807595?term=index&page=1&position=8) | <img src="icons/include.png" height="32" alt="Include"> |[Include](https://www.flaticon.com/free-icon/add_2921226) | <img src="icons/exclude.png" height="32" alt="Exclude">|[Exclude](https://www.flaticon.com/free-icon/remove_2921203) |
| <img src="icons/compare.png" height="32" alt="Compare">  | [Compare](https://www.flaticon.com/free-icon/file_748614?term=compare&page=1&position=17) | <img src="icons/clear_comparison.png" height="32" alt="Clear comparison"> |[Clear comparison](https://www.flaticon.com/free-icon/eraser_3277337?term=clear&page=1&position=5) |<img src="icons/instructions.png" height="32" alt="Help">  |[Help](https://www.flaticon.com/free-icon/information-point_4231321?term=help&page=1&position=87&page=1&position=87)|
| <img src="icons/main_canvas.png" height="32" alt="Main canvas">  | [Main canvas](https://www.flaticon.com/free-icon/image_3603103) | <img src="icons/compare_canvas.png" height="32" alt="Compare canvas"> |[Compare canvas](https://www.flaticon.com/free-icon/portraits_3603402) |  <img src="icons/preview_canvas.png" height="32" alt="Preview canvas">  |[Preview canvas](https://www.flaticon.com/free-icon/pieces_3603403)|
| <img src="icons/fingerprint.png" height="32" alt="Fingerprint">  | [Fingerprint](https://www.flaticon.com/free-icon/fingerprint_2313448?term=fingerprint&page=1&position=7) | <img src="icons/auto_zoom.png" height="32" alt="auto zoom"> | [Auto Zoom](https://www.flaticon.com/premium-icon/target_4723850?term=target%20lens&page=1&position=5&page=1&position=5&related_id=4723850&origin=search)  |  | |

## :e-mail: 联系

若有任何问题, 请提 issue 或者电邮 `xintao.wang@outlook.com`.
