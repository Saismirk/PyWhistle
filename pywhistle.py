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
SCROLL_LINE_FACTOR = 17
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


class ScrollableImage(ttk.Frame):
    def __init__(self, master=None, **kw):
        self.image = kw.pop('image', None)
        super(ScrollableImage, self).__init__(master=master, **kw)
        self.cnvs = Canvas(self, highlightthickness=0, **kw)
        self.cnvs.create_image(0, 0, anchor='nw', image=self.image)
        self.v_scroll = ttk.Scrollbar(self, orient='vertical')
        self.cnvs.grid(row=0, column=0,  sticky='nsew')
        self.v_scroll.grid(row=0, column=1, sticky='ns')
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.cnvs.config(yscrollcommand=self.v_scroll.set)
        self.v_scroll.config(command=self.cnvs.yview)
        self.cnvs.config(scrollregion=self.cnvs.bbox('all'))
        self.cnvs.bind_class(self.cnvs, "<MouseWheel>", self.mouse_scroll)

    def update_image(self, image):
        self.cnvs.delete("all")
        self.cnvs.create_image(0, 0, anchor='nw', image=image)
        self.cnvs.config(scrollregion=self.cnvs.bbox('all'))

    def mouse_scroll(self, evt):
        if evt.state == 0 :
            # self.cnvs.yview_scroll(-1*(evt.delta), 'units') # For MacOS
            self.cnvs.yview_scroll(int(-1*(evt.delta/120)), 'units') # For windows
        if evt.state == 1:
            # self.cnvs.xview_scroll(-1*(evt.delta), 'units') # For MacOS
            self.cnvs.xview_scroll(int(-1*(evt.delta/120)), 'units') # For windows


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
        self.notes_help_frame = None
        self.notes_tree = None
        self.parent = parent
        self.parent.title("Tin Whistle Tab Tools v0.1.1")
        self.key = StringVar()
        self.key.trace("w", lambda name, index, mode: self.update_note_tree())
        self.key.set(KEYS[1])

    def take_input(self):
        notes = str(self.inputtxt.get("1.0", "end-1c")).strip(" ").strip("\n")
        sheet = create()
        sheet.set_key(self.key.get())
        sheet.set_time(self.time.get())
        sheet.set_tempo(self.tempo.get())
        sheet.add_notes(notes)
        sheet.header.set_title(self.title.get()).set_composer(self.composer.get()).set_tag(self.copyright.get())
        return sheet

    def gen_pdf(self):
        sheet = self.take_input()
        if sheet == None:
            return
        output = sheet.output_pdf(self.output_directory.get() + "/" + self.filename.get())
        os.system(output)

    def update_png(self, image):
        self.preview_image = ImageTk.PhotoImage(Image.open(image))
        self.preview.update_image(self.preview_image)

    def gen_png(self):
        sheet = self.take_input()
        if sheet == None:
            return
        sheet.output_png(self.output_directory.get() + "/" + self.filename.get())

    def gen_preview_png(self):
        self.sheet = self.take_input()
        self.run_gen_png(os.getcwd() + "/" + "preview")

    def run_gen_png(self, path):
        self.sheet.output_png(path, self.update_png)

    def gen_midi(self):
        sheet = self.take_input()
        if sheet == None:
            return
        sheet.set_midi(True)
        fn = self.output_directory.get() + "/" + self.filename.get()
        sheet.output_png(fn)
        play_midi(fn + ".mid")

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
        self.check_scrollbar(event)
        char = event.widget.get("insert linestart", "insert")
        length = len(self.inputtxt.get("1.0", "end-1c"))
        if char != "" and length > 0:
            char = char[-1]
            if char not in ["1", "2", "3", "4", "5", "6", "7", "8", "0", ",", "h", "q", "w", "\'"]:
                self.inputtxt.edit_modified(False)
                return
            else:
                self.gen_preview_png()
                self.document_dirty = True
                self.inputtxt.edit_modified(False)
                return
        if self.inputtxt.edit_modified() and length == 0:
            self.gen_preview_png()
            self.document_dirty = True
        self.inputtxt.edit_modified(False)

    def scrollable_text_field(self, frame, height=100, default=""):
        self.txt_frame = Canvas(frame, highlightthickness=0, bd=0)
        self.txt_frame.pack(fill=BOTH, expand=True, padx=10, pady=5, anchor=N, side=LEFT)
        self.txt_scrollbar = ttk.Scrollbar(self.txt_frame)
        self.txt_scrollbar.pack(side=RIGHT, fill=Y)
        self.txt_frame.configure(yscrollcommand=self.txt_scrollbar.set)
        self.txt_scrollbar.configure(command=self.txt_frame.yview)
        self.txt = Text(self.txt_frame, highlightthickness=0, bd=0, undo=True, wrap=WORD)
        self.txt.insert(END, default)
        self.txt.config(height=height)
        self.txt.bind("<<Modified>>", self.text_change_update_preview)
        self.txt.configure(yscrollcommand=self.txt_scrollbar.set)
        self.txt.pack(fill=BOTH, expand=True, padx=2, pady=2)
        self.txt_scrollbar.configure(command=self.txt.yview)
        self.txt.bind("<Configure>", self.check_scrollbar)
        return self.txt, self.txt_frame

    def check_scrollbar(self, event):
        lines = len(self.inputtxt.get("1.0", END).split('\n'))
        if self.txt_frame.winfo_height()/SCROLL_LINE_FACTOR >= lines:
            self.txt_scrollbar.pack_forget()
        else:
            self.txt_scrollbar.pack(side=RIGHT, fill=Y, before=self.txt)

    @staticmethod
    def generate_button(frame, label, command, side=LEFT):
        b = ttk.Button(frame, text=label, command=command)
        b.pack(fill=X, padx=10, pady=10, side=side, expand=True)
        return b

    def display_image(self, image):
        self.preview_frame = ttk.LabelFrame(self.parent, text="Preview", padding=10)
        self.preview_frame.pack(fill=BOTH, expand=True, anchor=CENTER, padx=20, pady=2)
        label = ScrollableImage(self.preview_frame, image=self.preview_image)
        label.pack(fill=BOTH, expand=True, padx=10, pady=10, anchor=CENTER, side=LEFT)
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
        self.filename.insert(0, "Output")
        self.output_directory.delete(0, END)
        self.output_directory.insert(0, os.getcwd() + os.sep + "Output")
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
            self.parent.title("PyWhistle - " + os.path.basename(self.save_file_path))
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
            self.parent.title("PyWhistle - " + os.path.basename(self.save_file_path))
            self.document_dirty = False

    def load_file(self):
        load_path = filedialog.askopenfilename(initialdir=os.getcwd(), defaultextension=".json", filetypes=[("JSON", "*.json")])
        if load_path:
            save = PyWhistleSave.load(load_path)
            self.parent.title("PyWhistle - " + os.path.basename(load_path))
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

    def update_note_tree(self):
        if self.notes_help_frame is None or self.notes_tree is None:
            return
        self.notes_help_frame.config(text=f"Note Reference {self.key.get()}")
        self.notes_tree.delete(*self.notes_tree.get_children())
        key = None
        for whistle_key in TIN_WHISTLE_KEYS:
            if whistle_key.name == self.key.get():
                key = whistle_key
                break
        notes = sorted(key.notes, key=lambda x: x < "8", reverse=True)
        for note in notes:
            try:
                note_symbol = NOTE_DICT[key.notes[note].strip("\'").strip(",")]
                if note.endswith("+") | note.endswith("8"):
                    note_symbol = note_symbol.upper()
                self.notes_tree.insert("", "end", values=(note, note_symbol))
            except KeyError:
                pass

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

        self.inputtxt, notes_input_frame = self.scrollable_text_field(notes_frame, 5, default="")

        self.notes_help_frame = ttk.LabelFrame(notes_frame, padding=5, text=f"Notation Help {self.key.get()}")
        self.notes_help_frame.pack(fill=Y, padx=10, pady=5, side=RIGHT, anchor=N)
        self.notes_tree = ttk.Treeview(self.notes_help_frame)
        scrollbar = ttk.Scrollbar(self.notes_help_frame, orient=VERTICAL, command=self.notes_tree.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.notes_tree.configure(yscrollcommand=scrollbar.set)
        self.notes_tree.pack(fill=BOTH, padx=10, pady=5, side=TOP, anchor=N, expand=True)
        self.notes_tree["columns"] = ("Symbol", "Note")
        self.notes_tree.column("#0", width=0, stretch=NO)
        self.notes_tree.column("Symbol", anchor=CENTER, width=40)
        self.notes_tree.column("Note", anchor=CENTER, width=40)
        self.notes_tree.heading("#0", text="", anchor=CENTER)
        self.notes_tree.heading("Symbol", text="Holes", anchor=CENTER)
        self.notes_tree.heading("Note", text="Note", anchor=CENTER)
        self.update_note_tree()

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
