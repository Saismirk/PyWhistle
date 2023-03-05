import json
import subprocess
import os
import re
from dataclasses import dataclass
from typing import Dict, Tuple

SEMICIRCLE_PATH = "\override #'(filled . #t)\\path #0 #'((moveto 0 -0.7)(lineto 0 0.7)(curveto 0 0.7 0.7 0.7 0.7 0)(curveto 0.7 0 0.7 -0.7 0 -0.7)(closepath))"
PLUS_PATH = "\halign #-1.2 \\path #0.2 #'((moveto 0.6 0)(lineto -0.6 0)(moveto 0 0.6)(lineto 0 -0.6)) \\vspace #-0.4 "


@dataclass
class TinWhistleKey:
    name: str
    notes: Dict[str, str]

    @staticmethod
    def get_note_markup(note: str, high_octave=False) -> str:
        note_pattern = re.compile(r"([a-g](?:es|is)?)")
        note = note_pattern.match(note).group(1)
        sharp = None
        if note.endswith("es"):
            note = note[:-2]
            sharp = "\\flat"
        elif note.endswith("is"):
            note = note[:-2]
            sharp = "\\sharp"
        if high_octave:
            note = note.capitalize()
        if sharp:
            return f"\\concat{{\\tiny\"{note}\"\\teeny{sharp}}}"
        else:
            return f"\"{note}\""

    def get_note(self, note: str):
        note_name = self.notes[note]
        return note_name, self.get_note_markup(note_name, note.endswith("+") or note.startswith("8")), FINGERING_DICT[note]


def decode_key(key):
    if 'name' in key and 'notes' in key:
        return TinWhistleKey(key['name'], key['notes'])
    return key


def get_keys():
    with open('Resources/keys.json') as f:
        keys = json.load(f, object_hook=decode_key)
    return keys


TIN_WHISTLE_KEYS = get_keys()
AVAILABLE_KEYS = [key.name for key in TIN_WHISTLE_KEYS]


def get_key(key_name) -> TinWhistleKey | None:
    for key in TIN_WHISTLE_KEYS:
        if key.name == key_name:
            return key
    return None


def tw_hole(filled: int = 0) -> str:
    if filled == -1:
        return f"\\halign #-1 \combine {SEMICIRCLE_PATH} \\draw-circle #0.7 #0.1 ##f \\vspace #-0.3"
    filling = "##f" if filled == 0 else "##t"
    return f"\\halign #-1 \\draw-circle #0.7 #0.1 {filling} \\vspace #-0.35"


def tw_hole_markup(one=0, two=0, three=0, four=0, five=0, six=0) -> str:
    return """^\markup {{
        \lower #-3.2
        \dir-column {{
            overblow
            {5}
            {4}
            {3}
            \\vspace #+0.15
            {2}
            {1}
            {0}
            notemarkupid
        }}
    }}""".format(tw_hole(one), tw_hole(two), tw_hole(three), tw_hole(four), tw_hole(five), tw_hole(six))


TIN_WHISTLE_HOLES = {
    0: tw_hole_markup(0, 0, 0, 0, 0, 0),
    1: tw_hole_markup(1, 0, 0, 0, 0, 0),
    -1: tw_hole_markup(-1, 0, 0, 0, 0, 0),
    2: tw_hole_markup(1, 1, 0, 0, 0, 0),
    -2: tw_hole_markup(1, -1, 0, 0, 0, 0),
    3: tw_hole_markup(1, 1, 1, 0, 0, 0),
    -3: tw_hole_markup(1, 1, -1, 0, 0, 0),
    4: tw_hole_markup(1, 1, 1, 1, 0, 0),
    -4: tw_hole_markup(1, 1, 1, -1, 0, 0),
    5: tw_hole_markup(1, 1, 1, 1, 1, 0),
    -5: tw_hole_markup(1, 1, 1, 1, -1, 0),
    6: tw_hole_markup(1, 1, 1, 1, 1, 1),
    -6: tw_hole_markup(1, 1, 1, 1, 1, 1),
    7: tw_hole_markup(0, 1, 1, 0, 0, 0),
    8: tw_hole_markup(0, 1, 1, 1, 1, 1),
}


def get_woodwind_markup(index: int, overblown=False) -> str:
    return TIN_WHISTLE_HOLES[index].replace("overblow", (PLUS_PATH if overblown else "\" \" \\vspace #-0.4 ")) if index in TIN_WHISTLE_HOLES else \
        TIN_WHISTLE_HOLES[0]


FINGERING_DICT = {
    "6": get_woodwind_markup(6),
    "6+": get_woodwind_markup(6, True),
    "6,": get_woodwind_markup(-6),
    "5": get_woodwind_markup(5),
    "5+": get_woodwind_markup(5, True),
    "5,": get_woodwind_markup(-5),
    "4": get_woodwind_markup(4),
    "4+": get_woodwind_markup(4, True),
    "3": get_woodwind_markup(3),
    "3+": get_woodwind_markup(3, True),
    "3,": get_woodwind_markup(-3),
    "2": get_woodwind_markup(2),
    "2+": get_woodwind_markup(2, True),
    "2,": get_woodwind_markup(-2),
    "1": get_woodwind_markup(1),
    "1+": get_woodwind_markup(1, True),
    "1,": get_woodwind_markup(-1),
    "0": get_woodwind_markup(0),
    "0+": get_woodwind_markup(0, True),
    "0,": get_woodwind_markup(0),
    "7": get_woodwind_markup(7),
    "7+": get_woodwind_markup(7, True),
    "8": get_woodwind_markup(8),
    "8+": get_woodwind_markup(8, True),
}

NOTE_LENGTH_DICT = {
    "l": "\\longa",
    "w": "1",
    "ww": "\\breve",
    "h": "2",
    "h.": "2.",
    "q": "4",
    "q.": "4.",
    "q\'": "8",
    "q\'.": "8.",
    "q\'\'": "16",
    "q\'\'.": "16.",
    "q\'\'\'": "32",
    "q\'\'\'.": "32.",
    "q\'\'\'\'": "64",
    "q\'\'\'\'.": "64.",
    "q\'\'\'\'\'": "128",
    "q\'\'\'\'\'.": "128.",
    "q\'\'\'\'\'\'": "256",
    "q\'\'\'\'\'\'.": "256.",
    None: "",
}


def get_notes(key: str, notes: str) -> list[Tuple[str, Tuple[str, str, str], str]]:
    note_pattern = re.compile(r"([0-8][+,]?)((?:l|ww|w|h|q'{0,6})\.?)?")
    matches = note_pattern.finditer(notes)
    note_list = []
    for match in matches:
        try:
            note_list.append((match.group(1), (get_key(key).get_note(match.group(1))), NOTE_LENGTH_DICT[match.group(2)]))
        except KeyError:
            print("Invalid note: ", match.group(1))
    return note_list


KEY_DICT = {
    "D": "d",
    "Bb": "bes",
    "Eb": "ees",
    "E": "e",
    "A": "a",
    "F": "f",
    "C": "c",
    "G": "g",
    "Low F": "f,",
    "Low C": "c,",
    "Low D": "d,",
    "Loe E": "e,",
}


def get_note_name(hole: str, note: Tuple[str, str, str], rhythm: str, key: TinWhistleKey) -> str:
    return note[0] + rhythm + key.get_note(hole)[2].replace("notemarkupid", note[1]) if hole[0] in key.notes else ""


class Staff:
    def set_easy(self, easy: bool):
        self.easy = easy
        return self

    def set_time(self, time):
        self.time = "\\time " + time
        return self

    def set_tempo(self, tempo):
        self.tempo = tempo
        return self

    def set_key(self, key: str):
        self.key = key, "Major"
        return self

    def __init__(self) -> None:
        self.notes = []
        self.clef = "\\clef \"treble^8\" "
        self.key = "D", "Major"
        self.time = "\\time 4/4"
        self.tempo = "90"
        self.easy = False
        self.midi = False

    def set_clef(self, clef):
        self.clef = " \\clef " + clef + " "
        return self

    def add_notes(self, notes):
        self.notes = ["\t\t" + get_note_name(note, n, t, get_key(self.key[0])) + "\n" for note, n, t in get_notes(self.key[0], notes)]
        return self

    def get_staff(self):
        return """melody =  \\fixed bes'' {{
    \\once \\override TextScript.outside-staff-priority = ##f \\textLengthOn
    \\numericTimeSignature \\key {0} {1} {2} {3} {4} {8}
    {5}
}}
\\score {{
    \\new Staff \\with{{ 
        \\textLengthOn
        instrumentName = \markup {{
            \\center-column {{ "Tin Whistle"
                \\line {{ "Key of {6}" }}
            }}}}
        }}{{
        \\melody 
    }}
    \\layout {{
        indent = 2\cm
        \\context {{
            \\StaffGroup
            \\override StaffGrouper.staff-staff-spacing.basic-distance = #8
        }}
    }}
    {7}
}}""".format(
            KEY_DICT[self.key[0]],
            "\\" + self.key[1].lower() if self.key[1] != "" else "",
            "\\easyHeadsOn" if self.easy else "",
            self.time,
            self.clef,
            "".join(self.notes),
            self.key[0],
            f"\\midi {{\\tempo 4 = {self.tempo}}}" if self.midi else "",
            f"\\tempo 4 = {self.tempo}"
        )

    def __str__(self) -> str:
        return self.get_staff()


class Title:
    title = ""
    composer = ""
    tagline = ""

    def set_title(self, title):
        self.title = title
        return self

    def set_composer(self, composer):
        self.composer = composer
        return self

    def set_tag(self, tagline):
        self.tagline = tagline
        return self

    def get_title(self):
        body = "\\header {\n"
        body += "  title = \"" + self.title + "\"\n" if self.title != "" else ""
        body += "  composer = \"" + self.composer + "\"\n" if self.composer != "" else ""
        body += "  tagline = \"" + self.tagline + "\"\n" if self.tagline != "" else ""
        body += "}\n"
        return body

    def __str__(self) -> str:
        return self.get_title()


class Sheet:
    def __init__(self) -> None:
        self.staffs = None
        self.staff = Staff()
        self.header = Title()

    def get_header(self) -> str:
        return self.header.get_title()

    def add_notes(self, notes):
        self.staff.add_notes(notes)
        return self

    def get_staff(self) -> str:
        return self.staff.get_staff()

    def set_midi(self, midi: bool):
        self.staff.midi = midi
        return self

    def set_key(self, key):
        self.staff.set_key(key)
        return self

    def set_time(self, time):
        self.staff.set_time(time)
        return self

    def set_tempo(self, tempo):
        self.staff.set_tempo(tempo)
        return self

    def get_output(self, filename="output"):
        with open(f"{filename}.ly", "w") as f:
            f.write(self.get_header() + self.get_staff())
        print(self.get_header() + self.get_staff())
        dirname = os.path.abspath(os.getcwd())
        lilypath = os.path.join(dirname, 'LilyPond/usr/bin/lilypond.exe')
        return lilypath

    def output_pdf(self, filename="output"):
        subprocess.call([self.get_output(filename), "-o", os.path.dirname(filename), f"{filename}.ly"], shell=False)
        return filename + ".pdf"

    def output_png(self, filename="output"):
        path = self.get_output(filename)
        #Hide console on subprocess call
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.call([path, "--png", "-dresolution=90", "-o", os.path.dirname(filename), f"{filename}.ly"],
                        shell=False,
                        startupinfo=startupinfo)
        return filename + ".png"

    def __str__(self) -> str:
        return self.header.__str__() + self.staffs.__str__()


def create():
    return Sheet()
