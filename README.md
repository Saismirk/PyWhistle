# PyWhistle

PyWhistle is a Windows application that generates music sheets as PNGs, MIDI files, and PDFs using LilyPond with a graphical user interface that allows users to input notes as text and set up the output document.

## Build

To build PyWhistle, follow these steps:

1. Clone this repository to your local machine.
2. Install the required packages by running `pip install -r requirements.txt`.
3. Run `python .\setup.py build` to build the executable file.
4. The resulting executable will be located in the `build` directory.

## Usage

To use PyWhistle, unzip the contents and run 'pywhistle.exe' to launch the application.

In the app, input notes as numbers that denote the number of holes pressed (fingering) on the tin whistle, from 0 to 8 where 7 and 8 are special numbers for special fingerings. Other special characters can be used to change a note's length (w: Whole note, q: quarter note, q': Eighth Note, q'', 16th note, etc).

To generate a PNG, MIDI, or PDF output, use one of the following methods:

- From the File menu, select the desired output format.
- Use the following keyboard shortcuts: PNG (ctrl+g), MIDI (ctrl+m), PDF (ctrl+p).

## License

PyWhistle is licensed under the MIT License. See [LICENSE](LICENSE) for more information.
