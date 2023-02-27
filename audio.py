import asyncio
import os

DEFAULT_SF2 = 'Resources/sf2/Tin_Whistle_AIR.sf2'

async def play_midi(midi_file):
    dirname = os.path.dirname(__file__)
    fluid_path = os.path.join(dirname, 'fluidsynth/bin/fluidsynth.exe')
    sf2_path = os.path.join(dirname, DEFAULT_SF2)
    proc = await asyncio.create_subprocess_exec(
        fluid_path,'-i', sf2_path, midi_file, '-r', "44100",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)