import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["tkinter", "PIL", "TKinterModernThemes"],
                     "includes": ["conversion_tools", "audio"],
                     "include_files": ["Resources/", "fluidsynth/", "LilyPond/"]}

# GUI applications require a different base on Windows (the default is for a console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(name="PyWhistle",
      version="0.1.1",
      description="Tin Whistle Music Sheet Tool based on LilyPond",
      options={"build_exe": build_exe_options},
      executables=[Executable("pywhistle.py", base=base),
                   ])
