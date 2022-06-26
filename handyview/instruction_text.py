instruct_text = r'''
▶ Mouse Wheel
Mouse wheel:         Previous/Next image, step = 1
Ctrl + Mouse wheel:  Zoom in/out, ratio = 1.05
Shift + Mouse wheel: Fast previous/next image, step = 10
Ctrl + Shift + Mouse wheel: Control separate view for zoom in/out
Drag the scroll bar: Canvas movement of oversized images

▶ Direction Key ↑ ↓ ← →
Direction key ↑ ↓:  Zoom in/out, ratio = 1.05
Direction key ← →:  Previous/Next image, step = 1
Ctrl + ↑ ↓:         Vertical scrolling of oversized images
Ctrl + ← →:         Horizontal scrolling of oversized images
Shift + ↑ ↓:        Fast zoom in/out, ratio = 1.2
Shift +  ← →:       Fast previous/next image, step = 10
Ctrl + Shift + ↑ ↓: Control separate view for zoom in/out

▶ Other Keys
F9:                 Change background color (white or light gray)
R:                  Reset zoom ration to 1
C:                  (Compare): switch images under single-view compare mode
V:                  Switch images under single-view compare mode
    C and V are a pair, similar to Direction key ← →, but switch among folders
Z:                  Auto zoom
Shift + Z:          Cancel auto zoom
Space:              Next image
Backspace:          Previous image
Tab:                Switch the focused views
'''
instruct_text_cn = r'''
▶ 滚轮操作
鼠标滚轮:                图像切换, 上一张/下一张图像, 步长为1
Ctrl + 鼠标滚轮:         图像缩放, 放大/缩小, 倍率1.05
Shift + 鼠标滚轮:        快速图像切换 (步长为10)
Ctrl + Shift + 鼠标滚轮: 多视图下, 单独控制一个视图的缩放
鼠标拖拽滚动条:          超大图的画布移动

▶ 方向键操作
方向键 ↑ ↓:              图像缩放, 倍率1.05
方向键 ← →:              图像切换, 步长为1
Ctrl + 方向键 ↑ ↓:       超大图画布上下移动
Ctrl + 方向键 ← →:       超大图画布左右移动
Shift + 方向键 ↑ ↓:      快速图像缩放, 倍率1.2
Shift + 方向键 ← →:      快速图像切换, 步长为10
Ctrl + Shift + 方向键 ↑ ↓: 多视图下, 单独控制一个视图的缩放

▶ 其他键盘操作
F9:                      切换画布背景颜色, 白色/浅灰色
R:                       (Reset) 重置图像缩放为1
C:                       (Compare) 单视图比较模式下, 图像切换
V:                       单视图比较模式下, 图像切换.
    C和V是一对, 类似左右方向键切换, 只是在多个folder间切换
Z:                       自动缩放
Shift + Z:               取消自动缩放
Space:                   图像切换, 下一张图像
Backspace:               图像切换, 上一张图像
Tab:                     改变激活的图片查看窗口
'''
