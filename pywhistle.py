import asyncio
from tkinter import *
from tkinter import ttk

import TKinterModernThemes as tkmt

from PIL import Image, ImageTk

from audio import play_midi
from conversion_tools import *

LABEL_WIDTH = 10
KEYS = ["E", "Eb", "F", "D", "C", "B", "Bb", "A", "G#", "G", "Low F", "Low E", "Low Eb", "Low D", "Low C#", "Low C"]

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill=BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")


class Gui(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self)
        self.preview = None
        self.inputtxt = None
        self.time = None
        self.tempo = None
        self.filename = None
        self.copyright = None
        self.composer = None
        self.title = None
        self.tempo_pattern = None
        self.preview_image = None
        self.parent = parent
        self.parent.title("Tin Whistle Tab Tools v0.1.1")
        self.clicked = StringVar()
        self.clicked.set(KEYS[3])

    def take_input(self):
        NOTES = self.inputtxt.get("1.0", "end-1c")
        if NOTES == "":
            return None
        print(NOTES)
        sheet = create()
        sheet.set_key(self.clicked.get())
        sheet.set_time(self.time.get())
        sheet.set_tempo(self.tempo.get())
        sheet.add_notes(NOTES)
        sheet.header.set_title(self.title.get()
                               ).set_composer(self.composer.get()
                                              ).set_tag(self.copyright.get())
        return sheet

    def gen_pdf(self):
        sheet = self.take_input()
        if sheet == None:
            return
        output = sheet.output_pdf(self.filename.get())
        os.system(output)

    def update_png(self, image):
        self.preview_image = ImageTk.PhotoImage(Image.open(image))
        self.preview.image = self.preview_image
        self.preview.configure(image=self.preview_image)
        self.preview.update()

    def gen_png(self):
        sheet = self.take_input()
        if sheet == None:
            return
        output = sheet.output_png(self.filename.get())
        self.update_png(output)
        print(self.clicked.get())

    def gen_midi(self):
        sheet = self.take_input()
        if sheet == None:
            return
        sheet.set_midi(True)
        fn = self.filename.get()
        output = sheet.output_png(fn)
        self.update_png(output)
        asyncio.run(play_midi(fn + ".mid"))

    @staticmethod
    def text_field(frame, label, row=0, col=0, default=""):
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill=X, padx=10, pady=2)
        label_field = Label(text_frame, text=label, width=LABEL_WIDTH, anchor="w")
        label_field.pack(fill=X, padx=10, pady=2, side=LEFT)
        entry = ttk.Entry(text_frame)
        entry.pack(fill=X, padx=10, pady=2, side=LEFT, expand=True)
        entry.insert(0, default)
        return entry

    def scrollable_text_field(self, frame, height=100, row=0, col=0, default=""):
        f = ttk.LabelFrame(frame, text="Notes", padding=10)
        f.pack(fill=X, expand=True, padx=10, pady=5, anchor=N)
        txt = Text(f, highlightthickness=0, bd=0, undo=True, wrap=WORD)
        txt.insert(END, default)
        txt.config(height=height)
        txt.pack(fill=BOTH, expand=True, padx=2, pady=2)
        return txt

    def generate_button(self, frame, label, command):
        b = ttk.Button(frame, text=label, command=command)
        b.pack(fill=X, padx=10, pady=10, side=LEFT, expand=True)
        return b

    def display_image(self, image, row=0, col=0):
        preview_frame = ttk.LabelFrame(self.parent, text="Preview", padding=10)
        preview_frame.pack(fill=BOTH, expand=True, anchor=CENTER, padx=20, pady=2)
        scroll_frame = ScrollableFrame(preview_frame)
        label = Label(scroll_frame.scrollable_frame, text="Preview")
        label.image = self.preview_image
        label.configure(image=self.preview_image)
        label.pack(fill=BOTH, expand=True, padx=10, pady=2)
        scroll_frame.pack(fill=BOTH, expand=True, padx=10, pady=2, anchor=N)
        return label

    def entry_field(self, label, frame, validation, width=4, default="0"):
        entry_frame = ttk.Frame(frame)
        entry_frame.pack(fill=X, padx=10, pady=0, side=LEFT, anchor=CENTER)
        l = ttk.Label(entry_frame, text=label)
        l.pack(side=LEFT, anchor=CENTER, padx=10, pady=0)
        vcmd = (self.parent.register(validation),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        txt = ttk.Entry(entry_frame, validate='key', validatecommand=vcmd)
        txt.insert(0, default)
        txt.pack(side=LEFT, anchor=CENTER, padx=10, pady=0, expand=True)
        return txt

    def validate_float(self, action, index, value_if_allowed,
                       prior_value, text, validation_type, trigger_type, widget_name):
        if value_if_allowed:
            try:
                return float(value_if_allowed) > 0
            except ValueError:
                return False
        else:
            return False

    def validate_tempo(self, action, index, value_if_allowed,
                       prior_value, text, validation_type, trigger_type, widget_name):
        if value_if_allowed:
            try:
                matches = self.tempo_pattern.findall(str(value_if_allowed))
                return len(matches) == 1
            except ValueError:
                return False
        else:
            return False

    def options_field(self, label, frame, *options):
        options_frame = ttk.Frame(frame)
        options_frame.pack(fill=X, padx=10, pady=2, side=LEFT, anchor=CENTER)
        options_label = Label(options_frame, text=label)
        options_label.pack(side=LEFT, anchor=CENTER, padx=10, pady=2)
        txt = ttk.OptionMenu(options_frame, self.clicked, *options)
        txt.pack(side=LEFT, anchor=CENTER, padx=10, pady=2)

    def display_ui(self, parent):
        frame_inputs = ttk.Frame(parent)
        frame_inputs.pack(fill=X, padx=10, pady=10, anchor=N)
        self.preview_image = ImageTk.PhotoImage(Image.open("Resources/default.png"))
        self.tempo_pattern = re.compile(r"^[0-9]?\/[0-9]?$")
        frame_input = ttk.LabelFrame(frame_inputs, text="File Settings", padding=10)
        frame_input.pack(fill=X, padx=10, pady=5)
        self.title = self.text_field(frame_input, "Title", 0, 0, default="Untitled")
        self.composer = self.text_field(frame_input, "Composer", 1, 0)
        self.copyright = self.text_field(frame_input, "Copyright", 2, 0, default="Me")
        self.filename = self.text_field(frame_input, "Filename", 3, 0, default="output")

        frame_settings = ttk.LabelFrame(frame_inputs, padding=5, text="Sheet Settings")
        frame_settings.pack(fill=X, padx=10, pady=5, anchor=CENTER, expand=True)
        self.options_field("Key", frame_settings, *KEYS)
        self.tempo = self.entry_field("Tempo", frame_settings, self.validate_float, 4, default="180")
        self.time = self.entry_field("Time", frame_settings, self.validate_tempo, 8, default="3/4")

        self.inputtxt = self.scrollable_text_field(frame_inputs,
                                                   5,
                                                   row=7, col=0,
                                                   default="1q.5+q'12 3q55 1q.5+q'13 2q. 6+q'12 32176+1 252q7q''12q' 3q.2q'435w4q'321q 5+q'1235")

        frame_b = ttk.LabelFrame(frame_inputs, text="Output", padding=10)
        frame_b.pack(fill=X, padx=10, pady=5, anchor=N)
        self.generate_button(frame_b, "Generate PDF", lambda: self.gen_pdf())
        self.generate_button(frame_b, "Generate PNG", lambda: self.gen_png())
        self.generate_button(frame_b, "Play MIDI", lambda: self.gen_midi())

        self.preview = self.display_image(None, 9, 0)

        self.parent.mainloop()


if __name__ == "__main__":
    print("Starting PyWhistle...")
    try:
        window = tkmt.ThemedTKinterFrame("PyWhistle", "azure", "dark")
        window.root.title("")
        window.root.resizable(True, True)

        app = Gui(window.root)

        window.root.update()
        window.root.minsize(window.root.winfo_width(), window.root.winfo_height())

        window.root.geometry("900x1000")

        app.display_ui(window.root)
    except Exception as e:
        print(e)
