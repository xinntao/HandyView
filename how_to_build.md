## <img src="https://upload.wikimedia.org/wikipedia/commons/8/8d/Windows_darkblue_2012.svg" alt="Windows" height="28">

Use `pyinstaller` to compile to executable program, so that you can **double-click the image to open** the HandyView.

1. Use pyinstaller to build
   ```bash
    ./pyinstaller_install.sh
   ```
2. Choose the `dist/handyview/handyviewer.exe` as the default image viewer


## <img src="https://user-images.githubusercontent.com/11482921/171234862-5a54e430-7c07-4976-9ac8-ce8dbf520a17.png" alt="MacOS" height="24">

Using Anaconda for building will produce app with a very large file size, so we recommend using virtualenv to build the app.
1. Clone the repo
   ```bash
   git clone https://github.com/xinntao/HandyView.git
   cd HandyView
   ```
2. Prepare virtualenv
   ```bash
   pip3 install virtualenv
   virtualenv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Use pyinstaller to build
   ```bash
   ./pyinstaller_install_mac.sh
   ```
   the compiled app is located at `dist/handyviewer.app`
4. [option] Create dmg file
   ```bash
   ./create_dmg.sh
   ```
   the dmg file is located at `dist/handyviewer.dmg`
