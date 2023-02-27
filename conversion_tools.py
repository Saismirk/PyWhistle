import subprocess
import os
import re
from typing import Dict, Tuple

SEMICIRCLE_PATH = "\override #'(filled . #t)\\path #0 #'((moveto 0 -0.7)(lineto 0 0.7)(curveto 0 0.7 0.7 0.7 0.7 0)(curveto 0.7 0 0.7 -0.7 0 -0.7)(closepath))"
PLUS_PATH = "\halign #-1.2 \\path #0.2 #'((moveto 0.6 0)(lineto -0.6 0)(moveto 0 0.6)(lineto 0 -0.6)) \\vspace #-0.4 "


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
    return TIN_WHISTLE_HOLES[index].replace("overblow", (PLUS_PATH if overblown else "\" \" \\vspace #-0.4 ")) if index in TIN_WHISTLE_HOLES else TIN_WHISTLE_HOLES[0]


NOTE_DICT_D = {
    "6": ("d", "\"d\"", get_woodwind_markup(6)),
    "6+": ("d\'", "\"D\"", get_woodwind_markup(6, overblown=True)),
    "6,": ("dis", "\\concat{\\tiny\"d\"\\teeny\\sharp}", get_woodwind_markup(-6)),
    "5": ("e", "\"e\"", get_woodwind_markup(5)),
    "5+": ("e\'", "\"E\"", get_woodwind_markup(5, overblown=True)),
    "5,": ("f", "\"f\"", get_woodwind_markup(-5)),
    "4": ("fis", "\\concat{\\tiny\"f\"\\teeny\\sharp}", get_woodwind_markup(4)),
    "4+": ("fis\'", "\\concat{\\tiny\"F\"\\teeny\\sharp}", get_woodwind_markup(4, overblown=True)),
    "3": ("g", "\"g\"", get_woodwind_markup(3)),
    "3+": ("g\'", "\"G\"", get_woodwind_markup(3, overblown=True)),
    "3,": ("gis", "\\concat{\\tiny\"g\"\\teeny\\sharp}", get_woodwind_markup(-3)),
    "2": ("a", "\"a\"", get_woodwind_markup(2)),
    "2+": ("a\'", "\"a\"", get_woodwind_markup(2, overblown=True)),
    "2,": ("bes", "\\concat{\\tiny\"b\"\\teeny\\flat}", get_woodwind_markup(-2)),
    "1": ("b", "\"b\"", get_woodwind_markup(1)),
    "1+": ("b\'", "\"B\"", get_woodwind_markup(1, overblown=True)),
    "0": ("c\'", "\"c\"", get_woodwind_markup(0)),
    "0+": ("c\'\'", "\"C\"", get_woodwind_markup(0, overblown=True)),
    "7": ("cis\'", "\\concat{\\tiny\"c\"\\teeny\\sharp}", get_woodwind_markup(7)),
    "7+": ("cis\'\'", "\\concat{\\tiny\"C\"\\teeny\\sharp}", get_woodwind_markup(7, overblown=True)),
    "8": ("d\'", "\"D\"", get_woodwind_markup(8)),
    "8+": ("d\'\'", "\"D\"", get_woodwind_markup(8, overblown=True)),
}

NOTE_DICT_E = {
    "6": ("e", "\"e\"", get_woodwind_markup(6)),
    "6+": ("e\'", "\"E\"", get_woodwind_markup(6, overblown=True)),
    "6,": ("f", "\"f\"", get_woodwind_markup(-6)),
    "5": ("fis", "\\concat{\\tiny\"f\"\\teeny\\sharp}", get_woodwind_markup(5)),
    "5+": ("fis\'", "\\concat{\\tiny\"F\"\\teeny\\sharp}", get_woodwind_markup(5, overblown=True)),
    "5,": ("g", "\"g\"", get_woodwind_markup(-5)),
    "4": ("gis", "\\concat{\\tiny\"g\"\\teeny\\sharp}", get_woodwind_markup(4)),
    "4+": ("gis\'", "\\concat{\\tiny\"G\"\\teeny\\sharp}", get_woodwind_markup(4, overblown=True)),
    "3": ("a", "\"a\"", get_woodwind_markup(3)),
    "3+": ("a\'", "\"a\"", get_woodwind_markup(3, overblown=True)),
    "3,": ("bes", "\\concat{\\tiny\"b\"\\teeny\\flat}", get_woodwind_markup(-3)),
    "2": ("b", "\"b\"", get_woodwind_markup(2)),
    "2+": ("b\'", "\"B\"", get_woodwind_markup(2, overblown=True)),
    "2,": ("c\'", "\"c\"", get_woodwind_markup(-2)),
    "1": ("cis\'", "\\concat{\\tiny\"c\"\\teeny\\sharp}", get_woodwind_markup(1)),
    "1+": ("cis\'\'", "\\concat{\\tiny\"C\"\\teeny\\sharp}", get_woodwind_markup(1, overblown=True)),
    "0": ("d\'", "\"D\"", get_woodwind_markup(0)),
    "0+": ("d\'\'", "\"D\"", get_woodwind_markup(0, overblown=True)),
    "7": ("dis\'", "\\concat{\\tiny\"d\"\\teeny\\sharp}", get_woodwind_markup(7)),
    "7+": ("dis\'\'", "\\concat{\\tiny\"D\"\\teeny\\sharp}", get_woodwind_markup(7, overblown=True)),
    "8": ("e\'", "\"E\"", get_woodwind_markup(8)),
    "8+": ("e\'\'", "\"E\"", get_woodwind_markup(8, overblown=True)),
}

NOTE_DICT_EFLAT = {
    "6": ("ees", "\\concat{\\tiny\"e\"\\teeny\\flat}", get_woodwind_markup(6)),
    "6+": ("ees\'", "\\concat{\\tiny\"E\"\\teeny\\flat}", get_woodwind_markup(6, overblown=True)),
    "6,": ("f", "\"f\"", get_woodwind_markup(-6)),
    "5": ("f", "\"f\"", get_woodwind_markup(5)),
    "5+": ("f\'", "\"F\"", get_woodwind_markup(5, overblown=True)),
    "5,": ("ges", "\\concat{\\tiny\"g\"\\teeny\\flat}", get_woodwind_markup(-5)),
    "4": ("g", "\"g\"", get_woodwind_markup(4)),
    "4+": ("g\'", "\"G\"", get_woodwind_markup(4, overblown=True)),
    "3": ("aes", "\\concat{\\tiny\"a\"\\teeny\\flat}", get_woodwind_markup(3)),
    "3+": ("aes\'", "\\concat{\\tiny\"A\"\\teeny\\flat}", get_woodwind_markup(3, overblown=True)),
    "3,": ("bes", "\\concat{\\tiny\"b\"\\teeny\\flat}", get_woodwind_markup(-3)),
    "2": ("b", "\"b\"", get_woodwind_markup(2)),
    "2+": ("b\'", "\"B\"", get_woodwind_markup(2, overblown=True)),
    "2,": ("c", "\"c\"", get_woodwind_markup(-2)),
    "1": ("c", "\"c\"", get_woodwind_markup(1)),
    "1+": ("c\'", "\"C\"", get_woodwind_markup(1, overblown=True)),
    "0": ("d", "\"d\"", get_woodwind_markup(0)),
    "0+": ("d\'", "\"D\"", get_woodwind_markup(0, overblown=True)),
    "7": ("des", "\\concat{\\tiny\"d\"\\teeny\\flat}", get_woodwind_markup(7)),
    "7+": ("des\'", "\\concat{\\tiny\"D\"\\teeny\\flat}", get_woodwind_markup(7, overblown=True)),
    "8": ("e", "\"e\"", get_woodwind_markup(8)),
    "8+": ("e\'", "\"E\"", get_woodwind_markup(8, overblown=True)),
}

NOTE_DICT_F = {
    "6": ("f", "\"f\"", get_woodwind_markup(6)),
    "6+": ("f\'", "\"F\"", get_woodwind_markup(6, overblown=True)),
    "6,": ("ges", "\\concat{\\tiny\"g\"\\teeny\\flat}", get_woodwind_markup(-6)),
    "5": ("g", "\"g\"", get_woodwind_markup(5)),
    "5+": ("g\'", "\"G\"", get_woodwind_markup(5, overblown=True)),
    "5,": ("aes", "\\concat{\\tiny\"a\"\\teeny\\flat}", get_woodwind_markup(-5)),
    "4": ("a", "\"a\"", get_woodwind_markup(4)),
    "4+": ("a\'", "\"A\"", get_woodwind_markup(4, overblown=True)),
    "3": ("bes", "\\concat{\\tiny\"b\"\\teeny\\flat}", get_woodwind_markup(3)),
    "3+": ("bes\'", "\\concat{\\tiny\"B\"\\teeny\\flat}", get_woodwind_markup(3, overblown=True)),
    "3,": ("c", "\"c\"", get_woodwind_markup(-3)),
    "2": ("c", "\"c\"", get_woodwind_markup(2)),
    "2+": ("c\'", "\"C\"", get_woodwind_markup(2, overblown=True)),
    "2,": ("d", "\"d\"", get_woodwind_markup(-2)),
    "1": ("d", "\"d\"", get_woodwind_markup(1)),
    "1+": ("d\'", "\"D\"", get_woodwind_markup(1, overblown=True)),
    "0": ("e", "\"e\"", get_woodwind_markup(0)),
    "0+": ("e\'", "\"E\"", get_woodwind_markup(0, overblown=True)),
    "7": ("f", "\"f\"", get_woodwind_markup(7)),
    "7+": ("f\'", "\"F\"", get_woodwind_markup(7, overblown=True)),
    "8": ("fis", "\\concat{\\tiny\"f\"\\teeny\\sharp}", get_woodwind_markup(8)),
    "8+": ("fis\'", "\\concat{\\tiny\"F\"\\teeny\\sharp}", get_woodwind_markup(8, overblown=True)),
}

NOTE_DICT_C = {
    "6": ("c", "\"c\"", get_woodwind_markup(6)),
    "6+": ("c\'", "\"C\"", get_woodwind_markup(6, overblown=True)),
    "6,": ("d", "\"d\"", get_woodwind_markup(-6)),
    "5": ("d", "\"d\"", get_woodwind_markup(5)),
    "5+": ("d\'", "\"D\"", get_woodwind_markup(5, overblown=True)),
    "5,": ("ees", "\\concat{\\tiny\"e\"\\teeny\\flat}", get_woodwind_markup(-5)),
    "4": ("e", "\"e\"", get_woodwind_markup(4)),
    "4+": ("e\'", "\"E\"", get_woodwind_markup(4, overblown=True)),
    "3": ("f", "\"f\"", get_woodwind_markup(3)),
    "3+": ("f\'", "\"F\"", get_woodwind_markup(3, overblown=True)),
    "3,": ("ges", "\\concat{\\tiny\"g\"\\teeny\\flat}", get_woodwind_markup(-3)),
    "2": ("g", "\"g\"", get_woodwind_markup(2)),
    "2+": ("g\'", "\"G\"", get_woodwind_markup(2, overblown=True)),
    "2,": ("aes", "\\concat{\\tiny\"a\"\\teeny\\flat}", get_woodwind_markup(-2)),
    "1": ("a", "\"a\"", get_woodwind_markup(1)),
    "1+": ("a\'", "\"A\"", get_woodwind_markup(1, overblown=True)),
    "0": ("bes", "\\concat{\\tiny\"b\"\\teeny\\flat}", get_woodwind_markup(0)),
    "0+": ("bes\'", "\\concat{\\tiny\"B\"\\teeny\\flat}", get_woodwind_markup(0, overblown=True)),
    "7": ("c", "\"c\"", get_woodwind_markup(7)),
    "7+": ("c\'", "\"C\"", get_woodwind_markup(7, overblown=True)),
    "8": ("cis", "\\concat{\\tiny\"c\"\\teeny\\sharp}", get_woodwind_markup(8)),
    "8+": ("cis\'", "\\concat{\\tiny\"C\"\\teeny\\sharp}", get_woodwind_markup(8, overblown=True)),
}

NOTE_DICT_B = {
    "6": ("bes", "\\concat{\\tiny\"b\"\\teeny\\flat}", get_woodwind_markup(6)),
    "6+": ("bes\'", "\\concat{\\tiny\"B\"\\teeny\\flat}", get_woodwind_markup(6, overblown=True)),
    "6,": ("c", "\"c\"", get_woodwind_markup(-6)),
    "5": ("c", "\"c\"", get_woodwind_markup(5)),
    "5+": ("c\'", "\"C\"", get_woodwind_markup(5, overblown=True)),
    "5,": ("d", "\"d\"", get_woodwind_markup(-5)),
    "4": ("d", "\"d\"", get_woodwind_markup(4)),
    "4+": ("d\'", "\"D\"", get_woodwind_markup(4, overblown=True)),
    "3": ("ees", "\\concat{\\tiny\"e\"\\teeny\\flat}", get_woodwind_markup(3)),
    "3+": ("ees\'", "\\concat{\\tiny\"E\"\\teeny\\flat}", get_woodwind_markup(3, overblown=True)),
    "3,": ("f", "\"f\"", get_woodwind_markup(-3)),
    "2": ("f", "\"f\"", get_woodwind_markup(2)),
    "2+": ("f\'", "\"F\"", get_woodwind_markup(2, overblown=True)),
    "2,": ("ges", "\\concat{\\tiny\"g\"\\teeny\\flat}", get_woodwind_markup(-2)),
    "1": ("g", "\"g\"", get_woodwind_markup(1)),
    "1+": ("g\'", "\"G\"", get_woodwind_markup(1, overblown=True)),
    "0": ("aes", "\\concat{\\tiny\"a\"\\teeny\\flat}", get_woodwind_markup(0)),
    "0+": ("aes\'", "\\concat{\\tiny\"A\"\\teeny\\flat}", get_woodwind_markup(0, overblown=True)),
    "7": ("bes", "\\concat{\\tiny\"b\"\\teeny\\flat}", get_woodwind_markup(7)),
    "7+": ("bes\'", "\\concat{\\tiny\"B\"\\teeny\\flat}", get_woodwind_markup(7, overblown=True)),
    "8": ("c", "\"c\"", get_woodwind_markup(8)),
    "8+": ("c\'", "\"C\"", get_woodwind_markup(8, overblown=True)),
}

NOTE_DICT_A = {
    "6": ("aes", "\\concat{\\tiny\"a\"\\teeny\\flat}", get_woodwind_markup(6)),
    "6+": ("aes\'", "\\concat{\\tiny\"A\"\\teeny\\flat}", get_woodwind_markup(6, overblown=True)),
    "6,": ("bes", "\\concat{\\tiny\"b\"\\teeny\\flat}", get_woodwind_markup(-6)),
    "5": ("bes", "\\concat{\\tiny\"b\"\\teeny\\flat}", get_woodwind_markup(5)),
    "5+": ("bes\'", "\\concat{\\tiny\"B\"\\teeny\\flat}", get_woodwind_markup(5, overblown=True)),
    "5,": ("c", "\"c\"", get_woodwind_markup(-5)),
    "4": ("c", "\"c\"", get_woodwind_markup(4)),
    "4+": ("c\'", "\"C\"", get_woodwind_markup(4, overblown=True)),
    "3": ("cis", "\\concat{\\tiny\"c\"\\teeny\\sharp}", get_woodwind_markup(3)),
    "3+": ("cis\'", "\\concat{\\tiny\"C\"\\teeny\\sharp}", get_woodwind_markup(3, overblown=True)),
    "3,": ("d", "\"d\"", get_woodwind_markup(-3)),
    "2": ("d", "\"d\"", get_woodwind_markup(2)),
    "2+": ("d\'", "\"D\"", get_woodwind_markup(2, overblown=True)),
    "2,": ("ees", "\\concat{\\tiny\"e\"\\teeny\\flat}", get_woodwind_markup(-2)),
    "1": ("ees", "\\concat{\\tiny\"e\"\\teeny\\flat}", get_woodwind_markup(1)),
    "1+": ("ees\'", "\\concat{\\tiny\"E\"\\teeny\\flat}", get_woodwind_markup(1, overblown=True)),
    "1,": ("f", "\"f\"", get_woodwind_markup(-1)),
    "0": ("f", "\"f\"", get_woodwind_markup(0)),
    "0+": ("f\'", "\"F\"", get_woodwind_markup(0, overblown=True)),
    "7": ("ges", "\\concat{\\tiny\"g\"\\teeny\\flat}", get_woodwind_markup(7)),
    "7+": ("ges\'", "\\concat{\\tiny\"G\"\\teeny\\flat}", get_woodwind_markup(7, overblown=True)),
    "8": ("a", "\"a\"", get_woodwind_markup(8)),
    "8+": ("a\'", "\"A\"", get_woodwind_markup(8, overblown=True)),
}

NOTE_DICT_G = {
    "6": ("ges", "\\concat{\\tiny\"g\"\\teeny\\flat}", get_woodwind_markup(6)),
    "6+": ("ges\'", "\\concat{\\tiny\"G\"\\teeny\\flat}", get_woodwind_markup(6, overblown=True)),
    "6,": ("aes", "\\concat{\\tiny\"a\"\\teeny\\flat}", get_woodwind_markup(-6)),
    "5": ("aes", "\\concat{\\tiny\"a\"\\teeny\\flat}", get_woodwind_markup(5)),
    "5+": ("aes\'", "\\concat{\\tiny\"A\"\\teeny\\flat}", get_woodwind_markup(5, overblown=True)),
    "5,": ("bes", "\\concat{\\tiny\"b\"\\teeny\\flat}", get_woodwind_markup(-5)),
    "4": ("bes", "\\concat{\\tiny\"b\"\\teeny\\flat}", get_woodwind_markup(4)),
    "4+": ("bes\'", "\\concat{\\tiny\"B\"\\teeny\\flat}", get_woodwind_markup(4, overblown=True)),
    "3": ("c", "\"c\"", get_woodwind_markup(3)),
    "3+": ("c\'", "\"C\"", get_woodwind_markup(3, overblown=True)),
    "3,": ("cis", "\\concat{\\tiny\"c\"\\teeny\\sharp}", get_woodwind_markup(-3)),
    "2": ("cis", "\\concat{\\tiny\"c\"\\teeny\\sharp}", get_woodwind_markup(2)),
    "2+": ("cis\'", "\\concat{\\tiny\"C\"\\teeny\\sharp}", get_woodwind_markup(2, overblown=True)),
    "2,": ("d", "\"d\"", get_woodwind_markup(-2)),
    "1": ("d", "\"d\"", get_woodwind_markup(1)),
    "1+": ("d\'", "\"D\"", get_woodwind_markup(1, overblown=True)),
    "1,": ("ees", "\\concat{\\tiny\"e\"\\teeny\\flat}", get_woodwind_markup(-1)),
    "0": ("ees", "\\concat{\\tiny\"e\"\\teeny\\flat}", get_woodwind_markup(0)),
    "0+": ("ees\'", "\\concat{\\tiny\"E\"\\teeny\\flat}", get_woodwind_markup(0, overblown=True)),
    "7": ("f", "\"f\"", get_woodwind_markup(7)),
    "7+": ("f\'", "\"F\"", get_woodwind_markup(7, overblown=True)),
    "8": ("f", "\"f\"", get_woodwind_markup(8)),
    "8+": ("f\'", "\"F\"", get_woodwind_markup(8, overblown=True)),
}

NOTE_DICT_LOWF = {
    "6": ("f", "\"f\"", get_woodwind_markup(6)),
    "6+": ("f\'", "\"F\"", get_woodwind_markup(6, overblown=True)),
    "6,": ("ges", "\\concat{\\tiny\"g\"\\teeny\\flat}", get_woodwind_markup(-6)),
    "5": ("ges", "\\concat{\\tiny\"g\"\\teeny\\flat}", get_woodwind_markup(5)),
    "5+": ("ges\'", "\\concat{\\tiny\"G\"\\teeny\\flat}", get_woodwind_markup(5, overblown=True)),
    "5,": ("aes", "\\concat{\\tiny\"a\"\\teeny\\flat}", get_woodwind_markup(-5)),
    "4": ("aes", "\\concat{\\tiny\"a\"\\teeny\\flat}", get_woodwind_markup(4)),
    "4+": ("aes\'", "\\concat{\\tiny\"A\"\\teeny\\flat}", get_woodwind_markup(4, overblown=True)),
    "3": ("bes", "\\concat{\\tiny\"b\"\\teeny\\flat}", get_woodwind_markup(3)),
    "3+": ("bes\'", "\\concat{\\tiny\"B\"\\teeny\\flat}", get_woodwind_markup(3, overblown=True)),
    "3,": ("c", "\"c\"", get_woodwind_markup(-3)),
    "2": ("c", "\"c\"", get_woodwind_markup(2)),
    "2+": ("c\'", "\"C\"", get_woodwind_markup(2, overblown=True)),
    "2,": ("cis", "\\concat{\\tiny\"c\"\\teeny\\sharp}", get_woodwind_markup(-2)),
    "1": ("cis", "\\concat{\\tiny\"c\"\\teeny\\sharp}", get_woodwind_markup(1)),
    "1+": ("cis\'", "\\concat{\\tiny\"C\"\\teeny\\sharp}", get_woodwind_markup(1, overblown=True)),
    "1,": ("d", "\"d\"", get_woodwind_markup(-1)),
    "0": ("d", "\"d\"", get_woodwind_markup(0)),
    "0+": ("d\'", "\"D\"", get_woodwind_markup(0, overblown=True)),
    "7": ("ees", "\\concat{\\tiny\"e\"\\teeny\\flat}", get_woodwind_markup(7)),
    "7+": ("ees\'", "\\concat{\\tiny\"E\"\\teeny\\flat}", get_woodwind_markup(7, overblown=True)),
    "8": ("ees", "\\concat{\\tiny\"e\"\\teeny\\flat}", get_woodwind_markup(8)),
    "8+": ("ees\'", "\\concat{\\tiny\"E\"\\teeny\\flat}", get_woodwind_markup(8, overblown=True)),
}

NOTE_DICT_LOWE = {
    "6": ("ees", "\\concat{\\tiny\"e\"\\teeny\\flat}", get_woodwind_markup(6)),
    "6+": ("ees\'", "\\concat{\\tiny\"E\"\\teeny\\flat}", get_woodwind_markup(6, overblown=True)),
    "6,": ("f", "\"f\"", get_woodwind_markup(-6)),
    "5": ("f", "\"f\"", get_woodwind_markup(5)),
    "5+": ("f\'", "\"F\"", get_woodwind_markup(5, overblown=True)),
    "5,": ("ges", "\\concat{\\tiny\"g\"\\teeny\\flat}", get_woodwind_markup(-5)),
    "4": ("ges", "\\concat{\\tiny\"g\"\\teeny\\flat}", get_woodwind_markup(4)),
    "4+": ("ges\'", "\\concat{\\tiny\"G\"\\teeny\\flat}", get_woodwind_markup(4, overblown=True)),
    "3": ("aes", "\\concat{\\tiny\"a\"\\teeny\\flat}", get_woodwind_markup(3)),
    "3+": ("aes\'", "\\concat{\\tiny\"A\"\\teeny\\flat}", get_woodwind_markup(3, overblown=True)),
    "3,": ("bes", "\\concat{\\tiny\"b\"\\teeny\\flat}", get_woodwind_markup(-3)),
    "2": ("bes", "\\concat{\\tiny\"b\"\\teeny\\flat}", get_woodwind_markup(2)),
    "2+": ("bes\'", "\\concat{\\tiny\"B\"\\teeny\\flat}", get_woodwind_markup(2, overblown=True)),
    "2,": ("c", "\"c\"", get_woodwind_markup(-2)),
    "1": ("c", "\"c\"", get_woodwind_markup(1)),
    "1+": ("c\'", "\"C\"", get_woodwind_markup(1, overblown=True)),
    "1,": ("cis", "\\concat{\\tiny\"c\"\\teeny\\sharp}", get_woodwind_markup(-1)),
    "0": ("cis", "\\concat{\\tiny\"c\"\\teeny\\sharp}", get_woodwind_markup(0)),
    "0+": ("cis\'", "\\concat{\\tiny\"C\"\\teeny\\sharp}", get_woodwind_markup(0, overblown=True)),
    "7": ("d", "\"d\"", get_woodwind_markup(7)),
    "7+": ("d\'", "\"D\"", get_woodwind_markup(7, overblown=True)),
    "8": ("d", "\"d\"", get_woodwind_markup(8)),
    "8+": ("d\'", "\"D\"", get_woodwind_markup(8, overblown=True)),
}

NOTE_DICT_LOWD = {
    "6": ("f", "\"f\"", get_woodwind_markup(6)),
    "6+": ("f\'", "\"F\"", get_woodwind_markup(6, overblown=True)),
    "6,": ("ges", "\\concat{\\tiny\"g\"\\teeny\\flat}", get_woodwind_markup(-6)),
    "5": ("ges", "\\concat{\\tiny\"g\"\\teeny\\flat}", get_woodwind_markup(5)),
    "5+": ("ges\'", "\\concat{\\tiny\"G\"\\teeny\\flat}", get_woodwind_markup(5, overblown=True)),
    "5,": ("aes", "\\concat{\\tiny\"a\"\\teeny\\flat}", get_woodwind_markup(-5)),
    "4": ("aes", "\\concat{\\tiny\"a\"\\teeny\\flat}", get_woodwind_markup(4)),
    "4+": ("aes\'", "\\concat{\\tiny\"A\"\\teeny\\flat}", get_woodwind_markup(4, overblown=True)),
    "3": ("bes", "\\concat{\\tiny\"b\"\\teeny\\flat}", get_woodwind_markup(3)),
    "3+": ("bes\'", "\\concat{\\tiny\"B\"\\teeny\\flat}", get_woodwind_markup(3, overblown=True)),
    "3,": ("c", "\"c\"", get_woodwind_markup(-3)),
    "2": ("c", "\"c\"", get_woodwind_markup(2)),
    "2+": ("c\'", "\"C\"", get_woodwind_markup(2, overblown=True)),
    "2,": ("cis", "\\concat{\\tiny\"c\"\\teeny\\sharp}", get_woodwind_markup(-2)),
    "1": ("cis", "\\concat{\\tiny\"c\"\\teeny\\sharp}", get_woodwind_markup(1)),
    "1+": ("cis\'", "\\concat{\\tiny\"C\"\\teeny\\sharp}", get_woodwind_markup(1, overblown=True)),
    "1,": ("d", "\"d\"", get_woodwind_markup(-1)),
    "0": ("d", "\"d\"", get_woodwind_markup(0)),
    "0+": ("d\'", "\"D\"", get_woodwind_markup(0, overblown=True)),
    "7": ("ees", "\\concat{\\tiny\"e\"\\teeny\\flat}", get_woodwind_markup(7)),
    "7+": ("ees\'", "\\concat{\\tiny\"E\"\\teeny\\flat}", get_woodwind_markup(7, overblown=True)),
    "8": ("ees", "\\concat{\\tiny\"e\"\\teeny\\flat}", get_woodwind_markup(8)),
    "8+": ("ees\'", "\\concat{\\tiny\"E\"\\teeny\\flat}", get_woodwind_markup(8, overblown=True)),
}

NOTE_DICT_LOWC = {
    "6": ("f", "\"f\"", get_woodwind_markup(6)),
    "6+": ("f\'", "\"F\"", get_woodwind_markup(6, overblown=True)),
    "6,": ("ges", "\\concat{\\tiny\"g\"\\teeny\\flat}", get_woodwind_markup(-6)),
    "5": ("ges", "\\concat{\\tiny\"g\"\\teeny\\flat}", get_woodwind_markup(5)),
    "5+": ("ges\'", "\\concat{\\tiny\"G\"\\teeny\\flat}", get_woodwind_markup(5, overblown=True)),
    "5,": ("aes", "\\concat{\\tiny\"a\"\\teeny\\flat}", get_woodwind_markup(-5)),
    "4": ("aes", "\\concat{\\tiny\"a\"\\teeny\\flat}", get_woodwind_markup(4)),
    "4+": ("aes\'", "\\concat{\\tiny\"A\"\\teeny\\flat}", get_woodwind_markup(4, overblown=True)),
    "3": ("bes", "\\concat{\\tiny\"b\"\\teeny\\flat}", get_woodwind_markup(3)),
    "3+": ("bes\'", "\\concat{\\tiny\"B\"\\teeny\\flat}", get_woodwind_markup(3, overblown=True)),
    "3,": ("c", "\"c\"", get_woodwind_markup(-3)),
    "2": ("c", "\"c\"", get_woodwind_markup(2)),
    "2+": ("c\'", "\"C\"", get_woodwind_markup(2, overblown=True)),
    "2,": ("cis", "\\concat{\\tiny\"c\"\\teeny\\sharp}", get_woodwind_markup(-2)),
    "1": ("cis", "\\concat{\\tiny\"c\"\\teeny\\sharp}", get_woodwind_markup(1)),
    "1+": ("cis\'", "\\concat{\\tiny\"C\"\\teeny\\sharp}", get_woodwind_markup(1, overblown=True)),
    "1,": ("d", "\"d\"", get_woodwind_markup(-1)),
    "0": ("d", "\"d\"", get_woodwind_markup(0)),
    "0+": ("d\'", "\"D\"", get_woodwind_markup(0, overblown=True)),
    "7": ("ees", "\\concat{\\tiny\"e\"\\teeny\\flat}", get_woodwind_markup(7)),
    "7+": ("ees\'", "\\concat{\\tiny\"E\"\\teeny\\flat}", get_woodwind_markup(7, overblown=True)),
    "8": ("ees", "\\concat{\\tiny\"e\"\\teeny\\flat}", get_woodwind_markup(8)),
    "8+": ("ees\'", "\\concat{\\tiny\"E\"\\teeny\\flat}", get_woodwind_markup(8, overblown=True)),
}

NOTE_DICT_BFLAT = {
    "6": ("bes,", "\\concat{\\tiny\"b\"\\teeny\\flat}", get_woodwind_markup(6)),
    "6+": ("bes", "\\concat{\\tiny\"B\"\\teeny\\flat}", get_woodwind_markup(6, overblown=True)),
    "6,": ("b", "\"b\"", get_woodwind_markup(-6)),
    "5": ("c", "\"c\"", get_woodwind_markup(5)),
    "5+": ("c\'", "\"C\"", get_woodwind_markup(5, overblown=True)),
    "5,": ("cis", "\\concat{\\tiny\"c\"\\teeny\\sharp}", get_woodwind_markup(-5)),
    "4": ("d", "\"d\"", get_woodwind_markup(4)),
    "4+": ("d\'", "\"D\"", get_woodwind_markup(4, overblown=True)),
    "3": ("ees", "\\concat{\\tiny\"e\"\\teeny\\flat}", get_woodwind_markup(3)),
    "3+": ("ees\'", "\\concat{\\tiny\"E\"\\teeny\\flat}", get_woodwind_markup(3, overblown=True)),
    "3,": ("e", "\"e\"", get_woodwind_markup(-3)),
    "2": ("f", "\"f\"", get_woodwind_markup(2)),
    "2+": ("f\'", "\"F\"", get_woodwind_markup(2, overblown=True)),
    "2,": ("fis", "\\concat{\\tiny\"f\"\\teeny\\sharp}", get_woodwind_markup(-2)),
    "1": ("g", "\"g\"", get_woodwind_markup(1)),
    "1+": ("g\'", "\"G\"", get_woodwind_markup(1, overblown=True)),
    "1,": ("gis", "\\concat{\\tiny\"g\"\\teeny\\sharp}", get_woodwind_markup(-1)),
    "0": ("a", "\"a\"", get_woodwind_markup(0)),
    "0+": ("a\'", "\"A\"", get_woodwind_markup(0, overblown=True)),
    "7": ("aes", "\\concat{\\tiny\"a\"\\teeny\\flat}", get_woodwind_markup(7)),
    "7+": ("aes", "\\concat{\\tiny\"A\"\\teeny\\flat}", get_woodwind_markup(7, overblown=True)),
    "8": ("bes", "\\concat{\\tiny\"b\"\\teeny\\flat}", get_woodwind_markup(8)),
    "8+": ("bes\'\'", "\\concat{\\tiny\"B\"\\teeny\\flat}", get_woodwind_markup(8, overblown=True)),
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
            note_list.append((match.group(1), (NOTE_DICTS[key][match.group(1)]), NOTE_LENGTH_DICT[match.group(2)]))
        except KeyError:
            print("Invalid note: ", match.group(1))
    return note_list


NOTE_DICTS = {
    "D": NOTE_DICT_D,
    "Bb": NOTE_DICT_BFLAT,
    "Eb": NOTE_DICT_EFLAT,
    "E": NOTE_DICT_E,
    "A": NOTE_DICT_A,
    "F": NOTE_DICT_F,
    "C": NOTE_DICT_C,
    "G": NOTE_DICT_G,
    "Low F": NOTE_DICT_LOWF,
    "Low C": NOTE_DICT_LOWC,
    "Low D": NOTE_DICT_LOWD,
    "Loe E": NOTE_DICT_LOWE,
}

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


def get_note_name(hole: str, note: Tuple[str, str, str], rhythm: str, notes: Dict[str, str]) -> str:
    return note[0] + rhythm + notes[hole][2].replace("notemarkupid", note[1]) if hole[0] in notes else ""


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
        self.notes = ["\t\t" + get_note_name(note, n, t, NOTE_DICTS[self.key[0]]) + "\n" for note, n, t in get_notes(self.key[0], notes)]
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
        subprocess.call([self.get_output(filename), f"{filename}.ly"])
        return filename + ".pdf"

    def output_png(self, filename="output"):
        path = self.get_output(filename)
        subprocess.call([path, "--png", "-dresolution=90", f"{filename}.ly"])
        return filename + ".png"

    def __str__(self) -> str:
        return self.header.__str__() + self.staffs.__str__()


def create():
    return Sheet()
