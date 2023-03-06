import asyncio
import os
from tkinter import *
from tkinter import ttk
from tkinter import filedialog

import TKinterModernThemes as tkmt

from PIL import Image, ImageTk

import conversion_tools
from audio import play_midi
from conversion_tools import *

LABEL_WIDTH = 14
KEYS = conversion_tools.AVAILABLE_KEYS
KEYS.insert(0, "")


@dataclass()
class PyWhistleSave:
    filename: str
    output_directory: str
    composer: str
    copyright: str
    title: str
    notes: str
    time: str
    tempo: str
    key: str

    def save(self, file_path: str):
        with open(file_path, "w") as file:
            json.dump(self.__dict__, file, indent=4)

    @staticmethod
    def load(file_path: str):
        with open(file_path, "r") as file:
            data = json.load(file)
        return PyWhistleSave(**data)


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
        self.save_file_path = None
        self.opened_file_data = None
        self.sizegrip = None
        self.preview_frame = None
        self.settings_checkbutton = None
        self.show_settings = BooleanVar()
        self.preview = None
        self.inputtxt = None
        self.time = None
        self.tempo = None
        self.filename = None
        self.output_directory = None
        self.copyright = None
        self.composer = None
        self.title = None
        self.tempo_pattern = None
        self.preview_image = None
        self.gen_png_proc = None
        self.parent = parent
        self.parent.title("Tin Whistle Tab Tools v0.1.1")
        self.key = StringVar()
        self.key.set(KEYS[1])

    def take_input(self):
        notes = self.inputtxt.get("1.0", "end-1c")
        sheet = create()
        sheet.set_key(self.key.get())
        sheet.set_time(self.time.get())
        sheet.set_tempo(self.tempo.get())
        sheet.add_notes(notes)
        sheet.header.set_title(self.title.get()
                               ).set_composer(self.composer.get()
                                              ).set_tag(self.copyright.get())
        return sheet

    def gen_pdf(self):
        sheet = self.take_input()
        if sheet == None:
            return
        output = sheet.output_pdf(self.output_directory.get() + "/" + self.filename.get())
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
        output = sheet.output_png(self.output_directory.get() + "/" + self.filename.get())
        self.update_png(output)

    def gen_preview_png(self):
        self.sheet = self.take_input()
        self.run_gen_png()

    def run_gen_png(self):
        self.sheet.output_png(os.getcwd() + "/" + "preview", self.update_png)

    def gen_midi(self):
        sheet = self.take_input()
        if sheet == None:
            return
        sheet.set_midi(True)
        fn = self.output_directory.get() + "/" + self.filename.get()
        output = sheet.output_png(fn)
        self.update_png(output)
        asyncio.run(play_midi(fn + ".mid"))

    @staticmethod
    def text_field(frame, label, default="") -> ttk.Entry:
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill=X, padx=10, pady=2)
        label_field = Label(text_frame, text=label, width=LABEL_WIDTH, anchor="w")
        label_field.pack(fill=X, padx=10, pady=2, side=LEFT)
        entry = ttk.Entry(text_frame)
        entry.pack(fill=X, padx=10, pady=2, side=LEFT, expand=True)
        entry.insert(0, default)
        return entry

    def text_field_with_button(self, frame, label, button_label, default="") -> ttk.Entry:
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill=X, padx=10, pady=2)
        label_field = Label(text_frame, text=label, width=LABEL_WIDTH, anchor="w")
        label_field.pack(fill=X, padx=10, pady=2, side=LEFT)
        entry = ttk.Entry(text_frame)
        entry.pack(fill=X, padx=10, pady=2, side=LEFT, expand=True)
        entry.insert(0, default)
        button = ttk.Button(text_frame, text=button_label, command=lambda: self.browse_folder(entry.get(), entry))
        button.pack(fill=X, padx=10, pady=2, side=LEFT, expand=True)
        return entry

    def text_change_update_preview(self, event):
        if self.inputtxt.edit_modified():
            self.gen_preview_png()
            self.document_dirty = True
        self.inputtxt.edit_modified(False)

    def scrollable_text_field(self, frame, height=100, default=""):
        f = ttk.Frame(frame, padding=10)
        f.pack(fill=X, expand=True, padx=10, pady=5, anchor=N, side=LEFT)
        txt = Text(f, highlightthickness=0, bd=0, undo=True, wrap=WORD)
        txt.insert(END, default)
        txt.config(height=height)
        txt.bind("<<Modified>>", self.text_change_update_preview)
        txt.pack(fill=BOTH, expand=True, padx=2, pady=2)
        return txt, f

    @staticmethod
    def generate_button(frame, label, command, side=LEFT):
        b = ttk.Button(frame, text=label, command=command)
        b.pack(fill=X, padx=10, pady=10, side=side, expand=True)
        return b

    def display_image(self, image):
        self.preview_frame = ttk.LabelFrame(self.parent, text="Preview", padding=10)
        self.preview_frame.pack(fill=BOTH, expand=True, anchor=CENTER, padx=20, pady=2)
        scroll_frame = ScrollableFrame(self.preview_frame)
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

    @staticmethod
    def browse_folder(self, folder_path_var):
        folder_path = filedialog.askdirectory(initialdir=folder_path_var.get())
        if folder_path:
            folder_path_var.delete(0, END)
            folder_path_var.insert(0, folder_path)

    @staticmethod
    def validate_float(action, index, value_if_allowed,
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
                return re.match(self.tempo_pattern, str(value_if_allowed)) and float(matches[0]) > 0
            except ValueError:
                return False
        else:
            return False

    @staticmethod
    def set_entry_value(entry: Entry, value):
        entry.configure(validate="none")
        entry.delete(0, END)
        entry.insert(0, value)
        entry.configure(validate='key')

    def options_field(self, label, frame, *options):
        options_frame = ttk.Frame(frame)
        options_frame.pack(fill=X, padx=10, pady=2, side=LEFT, anchor=CENTER)
        options_label = Label(options_frame, text=label)
        options_label.pack(side=LEFT, anchor=CENTER, padx=10, pady=2)
        txt = ttk.OptionMenu(options_frame, self.key, *options)
        txt.pack(side=LEFT, anchor=CENTER, padx=10, pady=2)

    def toggle_settings(self):
        if not self.show_settings.get():
            self.main_frame.pack(fill=X, padx=10, pady=10, anchor=N, before=self.preview_toggle_frame)
        else:
            self.main_frame.pack_forget()

    def set_new_file(self):
        self.save_file_path = None
        self.opened_file_data = None
        self.filename.delete(0, END)
        self.output_directory.delete(0, END)
        self.composer.delete(0, END)
        self.copyright.delete(0, END)
        self.title.delete(0, END)
        self.inputtxt.delete(1.0, END)
        self.set_entry_value(self.time, "4/4")
        self.set_entry_value(self.tempo, "90")
        self.key.set(KEYS[1])
        self.save_file_path = None
        self.opened_file_data = None
        self.parent.title("PyWhistle - New File")

    def save_file(self):
        if not self.opened_file_data:
            self.save_file_as()
            return
        self.opened_file_data = PyWhistleSave(self.filename.get(), self.output_directory.get(), self.composer.get(), self.copyright.get(),
                                              self.title.get(), self.inputtxt.get(1.0, END), self.time.get(), self.tempo.get(), self.key.get())

        if self.save_file_path:
            self.opened_file_data.save(self.save_file_path)
            self.parent.title("PyWhistle - " + self.opened_file_data.filename)
            self.document_dirty = False

    def save_file_as(self):
        self.opened_file_data = PyWhistleSave(self.filename.get(), self.output_directory.get(), self.composer.get(), self.copyright.get(),
                                              self.title.get(), self.inputtxt.get(1.0, END), self.time.get(), self.tempo.get(), self.key.get())

        if self.save_file_path:
            new_path = filedialog.asksaveasfilename(initialdir=os.path.dirname(self.save_file_path),
                                                               defaultextension=".json", filetypes=[("JSON", "*.json")])
        else:
            new_path = filedialog.asksaveasfilename(initialdir=os.getcwd(), defaultextension=".json", filetypes=[("JSON", "*.json")])
        if new_path:
            self.save_file_path = new_path
            self.opened_file_data.save(self.save_file_path)
            self.parent.title("PyWhistle - " + self.opened_file_data.filename)
            self.document_dirty = False

    def load_file(self):
        load_path = filedialog.askopenfilename(initialdir=os.getcwd(), defaultextension=".json", filetypes=[("JSON", "*.json")])
        if load_path:
            save = PyWhistleSave.load(load_path)
            self.apply_file_settings(save)

    def apply_file_settings(self, save: PyWhistleSave):
        self.title.delete(0, END)
        self.title.insert(0, save.title)
        self.composer.delete(0, END)
        self.composer.insert(0, save.composer)
        self.copyright.delete(0, END)
        self.copyright.insert(0, save.copyright)
        self.output_directory.delete(0, END)
        self.output_directory.insert(0, save.output_directory)
        self.set_entry_value(self.tempo, save.tempo)
        self.set_entry_value(self.time, save.time)
        self.key.set(save.key)
        self.inputtxt.delete(1.0, END)
        self.inputtxt.insert(1.0, save.notes)
        self.parent.title(f"PyWhistle - {save.filename}")

    def display_ui(self, parent):
        self.main_frame = ttk.Frame(parent)
        self.main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        notes_buttons_frame = ttk.Frame(self.main_frame, width=100)
        notes_buttons_frame.pack(fill=X, padx=10, pady=5, side=TOP, anchor=N)
        file_menu = ttk.Menubutton(notes_buttons_frame, text="File")
        file_menu.menu = Menu(file_menu, tearoff=0)
        file_menu["menu"] = file_menu.menu
        file_menu.menu.add_command(label="New", command=lambda: self.set_new_file(), accelerator="Ctrl+N")
        file_menu.menu.add_command(label="Save", command=lambda: self.save_file(), accelerator="Ctrl+S")
        file_menu.menu.add_command(label="Save As..", command=lambda: self.save_file_as())
        file_menu.menu.add_command(label="Load", command=lambda: self.load_file(), accelerator="Ctrl+L")
        file_menu.menu.add_command(label="Generate PNG", command=lambda: self.gen_png(), accelerator="Ctrl+G")
        file_menu.menu.add_command(label="Generate MIDI", command=lambda: self.gen_midi(), accelerator="Ctrl+M")
        file_menu.menu.add_command(label="Generate PDF", command=lambda: self.gen_pdf(), accelerator="Ctrl+P")
        file_menu.pack(fill=X, padx=10, pady=0, side=LEFT, expand=False)
        self.parent.bind_all("<Control-n>", lambda event: self.set_new_file())
        self.parent.bind_all("<Control-s>", lambda event: self.save_file())
        self.parent.bind_all("<Control-l>", lambda event: self.load_file())
        self.parent.bind_all("<Control-g>", lambda event: self.gen_png())
        self.parent.bind_all("<Control-m>", lambda event: self.gen_midi())
        self.parent.bind_all("<Control-p>", lambda event: self.gen_pdf())

        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)
        self.frame_inputs = ttk.Frame(self.notebook)
        self.frame_inputs.pack(fill=X, padx=10, pady=10, anchor=N)

        self.preview_image = ImageTk.PhotoImage(Image.open("Resources/default.png"))
        self.tempo_pattern = re.compile(r"^[0-9]?\/[0-9]?$")
        frame_input = ttk.LabelFrame(self.frame_inputs, text="File Settings", padding=10)
        frame_input.pack(fill=X, padx=10, pady=5)
        self.title = self.text_field(frame_input, "Title", default="Untitled")
        self.composer = self.text_field(frame_input, "Composer")
        self.copyright = self.text_field(frame_input, "Copyright", default="Me")
        self.filename = self.text_field(frame_input, "Filename", default="output")
        self.output_directory = self.text_field_with_button(frame=frame_input, label="Output Directory", default=os.getcwd() + "\\Output",
                                                            button_label="Browse")

        frame_settings = ttk.LabelFrame(self.frame_inputs, padding=5, text="Sheet Settings")
        frame_settings.pack(fill=X, padx=10, pady=5, anchor=N, expand=True)

        self.options_field("Key", frame_settings, *KEYS)
        self.tempo = self.entry_field("Tempo", frame_settings, self.validate_float, 4, default="180")
        self.time = self.entry_field("Time", frame_settings, self.validate_tempo, 8, default="3/4")

        notes_frame = ttk.Frame(self.notebook, padding=5)
        notes_frame.pack(fill=BOTH, padx=10, pady=5, anchor=N)

        self.inputtxt, notes_input_frame = self.scrollable_text_field(notes_frame,
                                                                      5,
                                                                      default="")

        notes_help_frame = ttk.LabelFrame(notes_frame, padding=5, text=f"Notation Help {self.key.get()}")
        notes_help_frame.pack(fill=Y, padx=10, pady=5, side=RIGHT, anchor=N)
        notes_tree = ttk.Treeview(notes_help_frame)
        scrollbar = ttk.Scrollbar(notes_help_frame, orient=VERTICAL, command=notes_tree.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        notes_tree.configure(yscrollcommand=scrollbar.set)
        notes_tree.pack(fill=BOTH, padx=10, pady=5, side=TOP, anchor=N, expand=True)
        notes_tree["columns"] = ("Symbol", "Note")
        notes_tree.column("#0", width=0, stretch=NO)
        notes_tree.column("Symbol", anchor=CENTER, width=80)
        notes_tree.column("Note", anchor=CENTER, width=80)
        notes_tree.heading("#0", text="", anchor=CENTER)
        notes_tree.heading("Symbol", text="Holes", anchor=CENTER)
        notes_tree.heading("Note", text="Note", anchor=CENTER)
        key = None
        for Tkey in TIN_WHISTLE_KEYS:
            if Tkey.name == self.key.get():
                key = Tkey
                break
        # Sort notes by note name
        notes = sorted(key.notes, key=lambda x: x < "8", reverse=True)
        for note in notes:
            try:
                note_symbol = NOTE_DICT[key.notes[note].strip("\'").strip(",")]
                if note.endswith("+") | note.endswith("8"):
                    note_symbol = note_symbol.upper()
                notes_tree.insert("", "end", values=(note, note_symbol))
            except KeyError:
                pass

        self.notebook.add(notes_frame, text="Notes")
        self.notebook.add(self.frame_inputs, text="Document Settings")

        self.preview_toggle_frame = ttk.Frame(self.parent)
        self.preview_toggle_frame.pack(fill=X, padx=10, pady=5, anchor=N)
        ttk.Checkbutton(self.preview_toggle_frame,
                        text="Expand Preview",
                        style="Switch.TCheckbutton",
                        variable=self.show_settings,
                        command=self.toggle_settings).pack(fill=X, padx=10, pady=5, anchor=S)

        self.preview = self.display_image(None)

        self.sizegrip = ttk.Sizegrip(parent)
        self.sizegrip.pack(padx=(0, 5), pady=(0, 5), side=RIGHT, anchor=SE)


if __name__ == "__main__":
    try:
        window = tkmt.ThemedTKinterFrame("PyWhistle", "sun-valley", "dark")
        window.root.title("")
        window.root.iconbitmap("Resources/icon.ico")
        app = Gui(window.root)

        window.root.update()
        window.root.minsize(window.root.winfo_width(), window.root.winfo_height())

        window.root.geometry("900x1000")

        app.display_ui(window.root)
        app.set_new_file()
        window.run(cleanresize=True)
    except Exception as e:
        print(e)
