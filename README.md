<h1 align="center">ImageFlow</h1>

<p align="center">
  <b>Convert iPhone HEIC photos to JPG or PNG, in bulk, completely offline.</b><br>
  No upload, no account, no limits. Your photos never leave your computer.
</p>

<p align="center">
  <a href="https://github.com/achrafness/ImageFlow/releases/latest"><img src="https://img.shields.io/github/v/release/achrafness/ImageFlow" alt="Latest release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="MIT license"></a>
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-blue" alt="Windows, macOS and Linux">
</p>

<p align="center">
  <a href="https://github.com/achrafness/ImageFlow/releases/latest/download/ImageFlow-windows.exe"><b>Download for Windows</b></a>
  &nbsp;·&nbsp;
  <a href="https://github.com/achrafness/ImageFlow/releases/latest/download/ImageFlow-macos.zip"><b>Download for macOS</b></a>
  &nbsp;·&nbsp;
  <a href="https://github.com/achrafness/ImageFlow/releases/latest/download/ImageFlow-linux.tar.gz"><b>Download for Linux</b></a>
</p>

<p align="center">
  <img src="screenshots/demo.gif" alt="ImageFlow demo: adding images, choosing a format and converting" width="555">
</p>

## Why ImageFlow
Photos taken on an iPhone are saved as `.HEIC`, which Photoshop, many websites and older software cannot open. Online converters work, but uploading hundreds of photos is slow and hands your pictures to someone else's server. ImageFlow converts them on your own machine in one go.

## Features
- **Batch conversion:** convert hundreds of images in one click.
- **Drag and drop:** drop images or whole folders onto the window; folders are searched for images, including sub-folders.
- **8 formats:** JPG, JPEG, PNG, WEBP, TIFF, BMP, GIF and HEIC, both as input and output.
- **Fully offline:** nothing is uploaded and no internet connection is needed.
- **Safe by default:** existing files are never overwritten, a clashing name becomes `name (1).jpg`.
- **Keeps what matters:** EXIF metadata is preserved, and animated GIF / WEBP keep their frames.
- **Dark and light themes.**

## Install
Download the file for your system from the links above, or from the [latest release](https://github.com/achrafness/ImageFlow/releases/latest). Python is not required.

| System | How to run |
| --- | --- |
| Windows | Double-click `ImageFlow-windows.exe`. |
| macOS | Unzip `ImageFlow-macos.zip` and open `ImageFlow.app`. |
| Linux | `tar -xzf ImageFlow-linux.tar.gz && ./ImageFlow` |

The executables are not code-signed yet, so the first launch shows a warning:
- **Windows:** click *More info*, then *Run anyway*.
- **macOS:** right-click the app, choose *Open*, then *Open* again.

On Linux, if the app does not start with an error about the Qt `xcb` plugin, install one system package: `sudo apt install libxcb-cursor0`.

## Run from source
Requires Python 3.9 or newer.
```bash
git clone https://github.com/achrafness/ImageFlow.git
cd ImageFlow
python -m venv .venv
.venv/bin/pip install -r requirements.txt      # Windows: .venv\Scripts\pip
.venv/bin/python ImageFlow.py                  # Windows: .venv\Scripts\python
```

## Build the executable yourself
An executable has to be built on the system it is meant for:
```bash
pip install -r requirements.txt pyinstaller
pyinstaller ImageFlow.spec
```
The result is in the `dist` folder.

## Contributing
Bug reports, ideas and pull requests are welcome, please open an [issue](https://github.com/achrafness/ImageFlow/issues) first for bigger changes.

To publish a release, update the version in `version.py`, then push a matching tag (`git tag v1.2.0 && git push origin v1.2.0`). The `Build executables` workflow builds the Windows, macOS and Linux executables and attaches them to a new GitHub release.

## Built with
[PyQt6](https://pypi.org/project/PyQt6/), [Pillow](https://python-pillow.org/) and [pillow-heif](https://github.com/bigcat88/pillow_heif).

## Authors
Developed by Achraf Nessighaoui and Hamza Rouabah.

## License
[MIT](LICENSE)
