# Simple yt-dlp GUI

A lightweight desktop GUI for [yt-dlp](https://github.com/yt-dlp/yt-dlp), written in Python using Tkinter.

The application provides a simple graphical interface for downloading supported video and audio content without having to manually enter yt-dlp commands.

## Features

- Simple and lightweight Tkinter interface
- Video and playlist URL support
- Multiple quality options:
  - Best available
  - 1080p
  - 720p
- MP3 audio extraction
- Download progress indicator
- Custom output folder
- Optional Firefox cookie support
- YouTube EJS solver support
- Automatic yt-dlp updates on startup
- Manual yt-dlp update option
- Download log
- Stop running downloads
- Automatic MP4 merging when required

## Requirements

- Python 3
- yt-dlp
- yt-dlp-ejs
- Node.js
- FFmpeg

### Install Python Dependencies

Open PowerShell or Command Prompt and run:

```powershell
py -m pip install -U yt-dlp yt-dlp-ejs
```

### FFmpeg

FFmpeg is required for operations such as merging separate video and audio streams and converting audio to MP3.

Make sure FFmpeg is installed and available through your system `PATH`.

### Node.js

Node.js is used by the optional YouTube EJS solver functionality.

Make sure Node.js is installed and available through your system `PATH`.

## Run

Download or clone the repository and open PowerShell or Command Prompt in the directory containing `ytdl.py`.

Run:

```powershell
py ytdl.py
```

The graphical interface will open automatically.

## Usage

1. Enter a supported video or playlist URL.
2. Select the output directory.
3. Choose the desired quality.
4. Optionally enable:
   - **Audio only (MP3)**
   - **Use YouTube EJS solver**
   - **Use Firefox cookies**
   - **Auto-update yt-dlp on start**
5. Click **Download**.
6. Download progress and yt-dlp output will be displayed inside the application.

## Quality Options

### Best

Downloads the best available video and audio streams and merges them into an MP4 file when required.

### 1080p

Attempts to download the best available video up to 1080p together with the best available audio.

### 720p

Attempts to download the best available video up to 720p together with the best available audio.

### Audio / MP3

Extracts the audio stream and converts it to MP3 using the highest configured audio quality.

## Firefox Cookies

The optional **Use Firefox cookies** setting instructs yt-dlp to use cookies from the local Firefox browser profile.

This can be useful for content that requires an authenticated browser session.

The application itself does not store browser cookies.

## EJS Solver

The **Use YouTube EJS solver** option enables the yt-dlp EJS remote component using Node.js.

The application starts yt-dlp with:

```text
--js-runtimes node
--remote-components ejs:github
```

This option is enabled by default.

## Updating yt-dlp

By default, the application attempts to update `yt-dlp` and `yt-dlp-ejs` when it starts.

Automatic updating can be disabled by unchecking:

**Auto-update yt-dlp on start**

You can also manually trigger an update using:

**Update yt-dlp**

The equivalent command is:

```powershell
py -m pip install -U yt-dlp yt-dlp-ejs
```

## Output

Downloaded files are saved to the selected output directory.

The default output directory is:

```text
Downloads
```

Files use the title reported by yt-dlp as their filename.

## Troubleshooting

If a video is reported as unavailable even though you can access it normally in Firefox, try:

1. Log into the relevant website using Firefox.
2. Enable **Use Firefox cookies**.
3. Try the download again.

If yt-dlp is missing or outdated, use the **Update yt-dlp** button or run:

```powershell
py -m pip install -U yt-dlp yt-dlp-ejs
```

If video/audio merging or MP3 conversion fails, verify that FFmpeg is installed and available through your system `PATH`.

## Third-Party Software

This project provides a graphical interface for yt-dlp.

yt-dlp is a separate open-source project and is not developed, maintained, or affiliated with Nexovant.

For information about yt-dlp itself, including supported websites, features, and its licensing terms, see the official yt-dlp project.

## Responsible Use

Use this software only for content that you are authorized to access and download.

Users are responsible for complying with applicable terms, permissions, and copyright requirements.

## Copyright

Copyright © 2026 Nexovant. All rights reserved.

This source code is provided for viewing and educational purposes only.

Redistribution, modification, republication, sublicensing, or commercial use of this source code is not permitted without prior written permission from the copyright holder.
