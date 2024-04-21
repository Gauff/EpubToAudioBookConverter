**EPUB (Electronic Publication) to MP3 (Audio Book) Converter** 
============================================================

**Overview**
-----------

This is a Python program that converts EPUB files to MP3 audiobooks. It allows users to select the EPUB file, choose the voice and playback settings, and generate an MP3 file for each chapter or a single MP3 file containing all chapters.

![Screenshot](https://github.com/Gauff/EpubToAudioBookConverter/blob/master/screenshot.png)


**Features**
---------

* Convert EPUB files to MP3 audiobooks
* Select the EPUB file using a file dialog
* Choose from various voices and playback settings (using MS Edge TTS on Windows)
* Generate an MP3 file for each chapter or a single MP3 file containing all chapters
* Save the UI status to a JSON file

**Getting Started**
-------------------

1. Clone this repository: `git clone https://github.com/your-username/epub-to-mp3-converter.git`
2. Install the required dependencies: `pip install -r requirements.txt` (Note: This program only works on Windows)
3. Run the program: `python epub_to_mp3_converter.py`

**Usage**
---------

1. Select an EPUB file using the file dialog
2. Choose a voice and playback settings from the dropdown menus
3. Set the output directory path and file name
4. Select chapters
5. Click the "Generate" button to start the conversion process

**Configuration**
--------------

* The program saves its UI status to a JSON file named `ui_status.json`
* You can load the saved UI status by running the program again
* You can also customize the program's behavior by modifying the code

**Troubleshooting**
-------------------

* If you encounter any issues, please check the program's output log for errors
* If you need help or have questions, feel free to open an issue on this repository's GitHub page

**License**
---------

This program is licensed under the MIT License. See `license` for details.

**Note**
-----

This project was coded in a few hours as a personal exercise to learn rudiments of customtkinter. It is a small and simple program, and it may not be suitable for production use without further testing and refinement.

I hope this helps! Let me know if you'd like me to make any changes.
