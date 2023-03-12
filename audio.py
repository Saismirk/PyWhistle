import asyncio
import os
import subprocess
import threading

DEFAULT_SF2 = 'Resources/sf2/Tin_Whistle_AIR.sf2'
thread = None
subprocess_object = None


def play_midi(midi_file, on_complete=None):
    global thread
    check_output_folder(midi_file)
    dirname = os.path.abspath(os.getcwd())
    fluid_path = os.path.join(dirname, 'fluidsynth/bin/fluidsynth.exe')
    sf2_path = os.path.join(dirname, DEFAULT_SF2)

    if thread is not None and thread.is_alive():
        thread.join()
    thread = threading.Thread(target=start_play_subprocess, args=(fluid_path, sf2_path, midi_file, on_complete))
    thread.start()


def start_play_subprocess(path, filename, midi_file, on_complete=None):
    global subprocess_object
    if subprocess_object is not None:
        subprocess_object.kill()

    check_output_folder(filename)
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    args = [path, "-i", filename, midi_file, "-r", "44100"]
    subprocess_object = subprocess.Popen(args, shell=False, startupinfo=startupinfo)
    subprocess_object.wait()
    if on_complete is not None:
        on_complete()


def check_output_folder(filename):
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))
