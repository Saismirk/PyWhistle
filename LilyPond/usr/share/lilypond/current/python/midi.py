# This file is part of LilyPond, the GNU music typesetter.
#
# Copyright (C) 2001--2020 Han-Wen Nienhuys <hanwen@xs4all.nl>
#           Jan Nieuwenhuizen <janneke@gnu.org>
#
#
# LilyPond is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# LilyPond is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with LilyPond.  If not, see <http://www.gnu.org/licenses/>.

# import midi
# s = open ("s.midi").read ()
# midi.parse_track (s)
# midi.parse (s)
#
#
# returns a MIDI file as the tuple
#
#  ((format, division), TRACKLIST)          # division (>0) = TPQN*4
#                                           # or (<0) TBD
#
# each track is an EVENTLIST, where EVENT is
#
#   (time, (type, ARG1, [ARG2]))            # time = cumulative delta time
# MIDI event:
#   type = MIDI status+channel >= x80
# META-event  = xFF:
#   type = meta-event type <= x7F
#   ARG1 = length
#   ARG2 = data

import array
import struct


class error (Exception):
    pass

# class warning (Exception): pass


def _add_constants():
    channelVoiceMessages = (
        (0x80, "NOTE_OFF"),
        (0x90, "NOTE_ON"),
        (0xA0, "POLYPHONIC_KEY_PRESSURE"),
        (0xB0, "CONTROLLER_CHANGE"),
        (0xC0, "PROGRAM_CHANGE"),
        (0xD0, "CHANNEL_KEY_PRESSURE"),
        (0xE0, "PITCH_BEND"),
    )
    channelModeMessages = (
        (0x78, "ALL_SOUND_OFF"),
        (0x79, "RESET_ALL_CONTROLLERS"),
        (0x7A, "LOCAL_CONTROL"),
        (0x7B, "ALL_NOTES_OFF"),
        (0x7C, "OMNI_MODE_OFF"),
        (0x7D, "OMNI_MODE_ON"),
        (0x7E, "MONO_MODE_ON"),
        (0x7F, "POLY_MODE_ON"),
    )
    metaEvents = (
        (0x00, "SEQUENCE_NUMBER"),
        (0x01, "TEXT_EVENT"),
        (0x02, "COPYRIGHT_NOTICE"),
        (0x03, "SEQUENCE_TRACK_NAME"),
        (0x04, "INSTRUMENT_NAME"),
        (0x05, "LYRIC"),  # renamed LYRIC_DISPLAY MIDI RP-26
        (0x06, "MARKER"),
        (0x07, "CUE_POINT"),
        (0x08, "PROGRAM_NAME"),  # added MIDI RP-19
        (0X09, "DEVICE_NAME"),  # added MIDI RP-19
        (0x20, "MIDI_CHANNEL_PREFIX"),
        (0x21, "MIDI_PORT"),
        (0x2F, "END_OF_TRACK"),
        (0x51, "SET_TEMPO"),
        (0x54, "SMTPE_OFFSET"),
        (0x58, "TIME_SIGNATURE"),
        (0x59, "KEY_SIGNATURE"),
        (0x60, "XMF_PATCH_TYPE_PREFIX"),  # added MIDI RP-32
        (0x7F, "SEQUENCER_SPECIFIC_META_EVENT"),
        (0xFF, "META_EVENT"),
    )
    globals().update((desc, msg) for msg, desc in
                     channelVoiceMessages + channelModeMessages + metaEvents)


_add_constants()


def _get_variable_length_number(nextbyte, getbyte):
    sum = 0
    while nextbyte >= 0x80:
        sum = (sum + (nextbyte & 0x7F)) << 7
        nextbyte = getbyte()
    return sum + nextbyte


def _first_command_is_repeat(status, nextbyte, getbyte):
    raise error('the first midi command in the track is a repeat')


def _read_two_bytes(status, nextbyte, getbyte):
    return status, nextbyte


def _read_three_bytes(status, nextbyte, getbyte):
    return status, nextbyte, getbyte()


def _read_string(nextbyte, getbyte):
    length = _get_variable_length_number(nextbyte, getbyte)
    return ''.join(chr(getbyte()) for i in range(length))


def _read_f0_byte(status, nextbyte, getbyte):
    if status == 0xff:
        return status, nextbyte, _read_string(getbyte(), getbyte)
    return status, _read_string(nextbyte, getbyte)


_read_midi_event = (
    _first_command_is_repeat,  # 0
    None,  # 10
    None,  # 20
    None,  # 30
    None,  # 40
    None,  # 50
    None,  # 60 data entry???
    None,  # 70 all notes off???
    _read_three_bytes,  # 80 note off
    _read_three_bytes,  # 90 note on
    _read_three_bytes,  # a0 poly aftertouch
    _read_three_bytes,  # b0 control
    _read_two_bytes,  # c0 prog change
    _read_two_bytes,  # d0 ch aftertouch
    _read_three_bytes,  # e0 pitchwheel range
    _read_f0_byte,   # f0
)


def _parse_track_body(data, clocks_max):
    # This seems to be the fastest way of getting bytes in order as integers.
    dataiter = iter(array.array('B', data))
    getbyte = dataiter.__next__

    time = 0
    status = 0
    try:
        for nextbyte in dataiter:
            time += _get_variable_length_number(nextbyte, getbyte)
            if clocks_max and time > clocks_max:
                break
            nextbyte = getbyte()
            if nextbyte >= 0x80:
                status = nextbyte
                nextbyte = getbyte()
            yield time, _read_midi_event[status >> 4](status, nextbyte, getbyte)
    except StopIteration:
        # If the track ended just before the start of an event, the for loop
        # will exit normally. If it ends anywhere else, we end up here.
        print(len(list(dataiter)))
        raise error('a track ended in the middle of a MIDI command')


def _parse_hunk(data, pos, type, magic):
    if data[pos:pos+4] != magic:
        raise error('expected %r, got %r' % (magic, data[pos:pos+4]))
    try:
        length, = struct.unpack('>I', data[pos+4:pos+8])
    except struct.error:
        raise error(
            'the %s header is truncated (may be an incomplete download)' % type)
    endpos = pos + 8 + length
    data = data[pos+8:endpos]
    if len(data) != length:
        raise error(
            'the %s is truncated (may be an incomplete download)' % type)
    return data, endpos


def _parse_tracks(midi, pos, num_tracks, clocks_max):
    if num_tracks > 256:
        raise error('too many tracks: %d' % num_tracks)
    for i in range(num_tracks):
        trackdata, pos = _parse_hunk(midi, pos, 'track', b'MTrk')
        yield list(_parse_track_body(trackdata, clocks_max))
    # if pos < len(midi):
    #     warn


def parse_track(track, clocks_max=None):
    track_body, end = _parse_hunk(track, 0, 'track', b'MTrk')
    # if end < len(track):
    #     warn
    return list(_parse_track_body(track_body, clocks_max))


def parse(midi, clocks_max=None):
    header, first_track_pos = _parse_hunk(midi, 0, 'file', b'MThd')
    try:
        format, num_tracks, division = struct.unpack('>3H', header[:6])
    except struct.error:
        raise error('the file header is too short')
#  if division < 0:
#    raise error ('cannot handle non-metrical time')
    tracks = list(_parse_tracks(midi, first_track_pos, num_tracks, clocks_max))
    return (format, division*4), tracks
