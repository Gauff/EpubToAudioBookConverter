import os
import tkinter as tk
from tkinter import filedialog
import customtkinter
import customtkinter as ctk
from CTkListbox import *
import json
import file_management
import my_edge_tts
import epub_reader
import lists


class EpubAudioConverterUI(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("EPUB (Electronic Publication) to MP3 (Audio Book) converter")

        self.geometry("1024x1024")
        customtkinter.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"

        # Variables
        self.epub_file_path = tk.StringVar()
        self.voice_var = tk.StringVar()
        self.output_directory_path = tk.StringVar()
        self.output_file_name = tk.StringVar()
        self.playback_speed_percentage = tk.DoubleVar(value=100)
        self.volume_percentage = tk.DoubleVar(value=100)
        self.pitch_hz = tk.DoubleVar(value=0)
        self.selected_chapter_text = tk.StringVar()
        self.book_title = tk.StringVar()
        self.chapter_text_by_filename = {}  # filename as key, text as value
        self.chapter_listbox_last_selection = None
        self.default_pad_x = 10
        self.default_pad_y = 10
        self.output_in_one_file_var = customtkinter.StringVar(value="off")

        # Load previous UI status
        self.load_ui_status()

        # Main Frame
        self.main_frame = ctk.CTkFrame(self)

        self._configure_grid()

        row_number = 0

        # Epub File Path
        self.epub_file_label = self._create_label("EPUB File Path:", row_number)
        self.epub_file_entry = self._create_entry(self.epub_file_path, row_number)
        self.epub_file_entry.bind("<Enter>", self._on_enter)
        self.epub_file_button = self._create_button("Browse", row_number, self._browse_epub_file)

        # Language Dropdown
        row_number += 1
        self.voice_label = self._create_label("Voice:", row_number)
        self.voice_option = sorted(my_edge_tts.load_voices())
        self.voice_dropdown = ctk.CTkOptionMenu(self.main_frame, values=self.voice_option, variable=self.voice_var)
        self.voice_dropdown.grid(row=row_number, column=1, sticky="we")

        # Output Directory Path
        row_number += 1
        self.output_directory_label = self._create_label("Output Directory Path:", row_number)
        self.output_directory_entry = self._create_entry(self.output_directory_path, row_number)
        self.output_directory_button = self._create_button("Browse", row_number, self._browse_output_directory)

        # Output File Name
        row_number += 1
        self.output_file_label = self._create_label("Output File Name:", row_number)
        self.output_file_entry = self._create_entry(self.output_file_name, row_number)
        self.output_in_one_file = customtkinter.CTkCheckBox(self.main_frame, text="Single MP3 file",
                                                            command=self._output_in_one_file_event,
                                                            variable=self.output_in_one_file_var, onvalue="on",
                                                            offvalue="off")
        self.output_in_one_file.grid(row=row_number, column=2, sticky="ew")

        # Playback Speed Percentage
        row_number += 1
        self.playback_speed_label = self._create_label("Playback Speed Percentage:", row_number)
        self.playback_speed_slider = self._create_slider(self.playback_speed_percentage, row_number, 0, 100)
        self.playback_speed_value_label = self._create_label("100%", row_number, column=2)

        # Volume Percentage
        row_number += 1
        self.volume_label = self._create_label("Volume Percentage:", row_number)
        self.volume_slider = self._create_slider(self.volume_percentage, row_number, 50, 200)
        self.volume_value_label = self._create_label("100%", row_number, column=2)

        # Pitch Hz
        row_number += 1
        self.pitch_label = self._create_label("Pitch Hz:", row_number)
        self.pitch_slider = self._create_slider(self.pitch_hz, row_number, -200, 200)
        self.pitch_value_label = self._create_label("0Hz", row_number, column=2)

        # Book title
        row_number += 1
        self.book_title_label = self._create_label("Book title:", row_number)
        self.book_title_value_label = self._create_entry(self.book_title, row_number)
        self.select_all_button = self._create_button("Select All", row_number, self._select_all_chapters)

        # Chapter List
        row_number += 1

        small_font = customtkinter.CTkFont(size=11)

        self.chapter_list_label = self._create_label("Chapter List:", row_number)
        # https://github.com/Akascape/CTkListbox
        self.chapter_listbox = CTkListbox(self.main_frame, command=self._display_selected_chapter_text,
                                          multiple_selection=True, font=small_font)
        self.chapter_listbox.grid(row=row_number, column=1, sticky="nswe")

        self.unselect_all_button = self._create_button("Unselect All", row_number, self._unselect_all_chapters, "ne")

        # Selected Chapter Text
        row_number += 1
        self.selected_chapter_label = self._create_label("Selected Chapter Text:", row_number)

        self.selected_chapter_text_box = ctk.CTkTextbox(self.main_frame, wrap=tk.WORD, padx=self.default_pad_x,
                                                        pady=self.default_pad_y)
        self.selected_chapter_text_box.insert(tk.END, self.selected_chapter_text.get())
        self.selected_chapter_text_box.grid(row=row_number, column=1, columnspan=2, sticky="nsew")

        # Buttons
        row_number += 1
        self.generate_button = self._create_button("Generate", row_number, self._generate, column=0, sticky="ew", columnspan=3)

        # Log
        row_number += 1
        self.log_label = self._create_label("", row_number, column=0, columnspan=3)

        # Save UI status when closing
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Bind the event handler for changes in epub_file_path
        self.epub_file_path.trace_add("write", self._on_epub_file_path_change)
        self.playback_speed_percentage.trace_add("write", self._update_playback_speed_label)
        self.volume_percentage.trace_add("write", self._update_volume_percentage_label)
        self.pitch_hz.trace_add("write", self._update_pitch_value_label)

        self.load_epub_file_chapters()

    def _configure_grid(self):
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        #  configure the row and column weights of the root window, respectively.
        #  This tells Tkinter to allocate any extra space to the first row and column, which contains main_frame.
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        # configure the row and column weights of main_frame, allowing it to resize along with its parent container.
        self.main_frame.grid_rowconfigure(8, weight=1)
        self.main_frame.grid_rowconfigure(9, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1, pad=10)

    def _create_label(self, text, row_number, column=0, columnspan=1):
        label = ctk.CTkLabel(self.main_frame, text=text, padx=self.default_pad_x, pady=self.default_pad_y)
        label.grid(row=row_number, column=column, sticky="w", columnspan=columnspan)
        return label

    def _create_entry(self, text_variable, row_number):
        entry = ctk.CTkEntry(self.main_frame, textvariable=text_variable)
        entry.grid(row=row_number, column=1, sticky="we")
        return entry

    def _create_button(self, text, row_number, command, sticky="e", column=2, columnspan=1):
        button = ctk.CTkButton(self.main_frame, text=text, command=command)
        button.grid(row=row_number, column=column, sticky=sticky, columnspan=columnspan)
        return button

    def _create_slider(self, variable, row_number, from_, to):
        slider = ctk.CTkSlider(self.main_frame, variable=variable, from_=from_, to=to)
        slider.grid(row=row_number, column=1, sticky="we")
        return slider

    def _log(self, text):
        self.log_label.configure(text=text)
        self.main_frame.update()

    def _update_pitch_value_label(self, *args):
        pitch = int(self.pitch_hz.get())
        self.pitch_value_label.configure(text=f"{pitch}Hz")

    def _update_playback_speed_label(self, *args):
        playback_speed = int(self.playback_speed_percentage.get())
        self.playback_speed_value_label.configure(text=f"{playback_speed}%")

    def _update_volume_percentage_label(self, *args):
        volume = int(self.volume_percentage.get())
        self.volume_value_label.configure(text=f"{volume}%")

    def _browse_epub_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("EPUB files", "*.epub")],
                                               initialdir=os.path.dirname(self.epub_file_path.get()))
        file_path = os.path.normpath(file_path)
        if file_path:
            self.epub_file_path.set(file_path)

    def _browse_output_directory(self):
        directory_path = filedialog.askdirectory()
        directory_path = os.path.normpath(directory_path)
        if directory_path:
            self.output_directory_path.set(directory_path)

    def _on_enter(self, event):
        self._on_drop(event)

    def _on_drop(self, event):
        if hasattr(event, "data"):
            file_path = event.widget.tk.splitlist(event.data.strip())[0]
            if file_path.lower().endswith('.epub'):
                self.epub_file_path.set(file_path)

    def _output_in_one_file_event(self, event):
        self.output_in_one_file_var.get()

    def _display_selected_chapter_text(self, event):

        if event is None:
            return

        if len(event) == 0:
            self.chapter_listbox_last_selection = None
            self.selected_chapter_text_box.delete('1.0', tk.END)
            return

        if len(event) == 1:
            file_name = event[0]
            text = str(self.chapter_text_by_filename[file_name]).strip()
            self.selected_chapter_text_box.delete('1.0', tk.END)
            self.selected_chapter_text_box.insert(tk.END, text)
            self.chapter_listbox_last_selection = event
            return

        if self.chapter_listbox_last_selection is not None:
            difference1, difference2 = lists.find_difference(self.chapter_listbox_last_selection, event)
            file_name = None
            if len(difference1) == 1:
                file_name = difference1[0]
            if len(difference2) == 1:
                file_name = difference2[0]
            if file_name is not None:
                text = str(self.chapter_text_by_filename[file_name]).strip()
                self.selected_chapter_text_box.delete('1.0', tk.END)
                self.selected_chapter_text_box.insert(tk.END, text)
            self.chapter_listbox_last_selection = event

    def _generate(self):

        file_name = self.output_file_name.get()

        if self.output_in_one_file_var.get() == "on":
            total = 1
            chapter_files = [x._text for x in self.chapter_listbox.selections]
            chapter_texts = [str(self.chapter_text_by_filename[chapter_file]).strip() for chapter_file in chapter_files]
            text = "\n\n".join(chapter_texts)
            self._generate_one_mp3_file(text, file_name, 1, total)
        else:
            total = len(list(self.chapter_listbox.curselection()))
            i = 0
            for index, chapter_file in zip(
                    list(self.chapter_listbox.curselection()),
                    [x._text for x in self.chapter_listbox.selections]):
                i = i + 1
                chapter_text = str(self.chapter_text_by_filename[chapter_file]).strip()

                self._generate_one_mp3_file(chapter_text, file_name, i, total)

        file_management.open_directory_in_explorer(self.output_directory_path.get())
        self._log(f"Audio book successfully created !")

    def _generate_one_mp3_file(self, text, file_name, index, total):

        temporary_file_path = os.path.normpath(file_management.create_temp_text_file(text))

        if index == total:
            file_name = f"{file_name}.mp3"
        else:
            file_name = f"{file_name} - {str(index).zfill(3)}.mp3"

        mp3_file_path = os.path.normpath(os.path.join(self.output_directory_path.get(), file_name))

        self._log(f"Generating {str(index).zfill(3)}/{str(total).zfill(3)} : {mp3_file_path}")

        my_edge_tts.generate_mp3_file(
            temporary_file_path,
            mp3_file_path,
            self.voice_var.get(),
            int(self.playback_speed_percentage.get()),
            int(self.volume_percentage.get()),
            int(self.pitch_hz.get()))

        file_management.delete_temp_file(temporary_file_path)

    def load_ui_status(self):
        try:
            with open("../ui_status.json", "r") as file:
                ui_status = json.load(file)
                self.epub_file_path.set(ui_status["epub_file_path"])
                self.voice_var.set(ui_status["voice_var"])
                self.output_directory_path.set(ui_status["output_directory_path"])
                self.output_file_name.set(ui_status["output_file_name"])
                self.playback_speed_percentage.set(ui_status["playback_speed_percentage"])
                self.volume_percentage.set(ui_status["volume_percentage"])
                self.pitch_hz.set(ui_status["pitch_hz"])
                self.output_in_one_file_var.set(ui_status.get("output_in_one_file", "on")),
                self.geometry(ui_status.get("geometry", "1024x1024"))

        except FileNotFoundError:
            pass  # If file does not exist, ignore and use default UI status

    def save_ui_status(self):
        ui_status = {
            "epub_file_path": self.epub_file_entry.get(),
            "voice_var": self.voice_dropdown.get(),
            "output_directory_path": self.output_directory_entry.get(),
            "output_file_name": self.output_file_entry.get(),
            "playback_speed_percentage": self.playback_speed_slider.get(),
            "volume_percentage": self.volume_slider.get(),
            "pitch_hz": self.pitch_slider.get(),
            "output_in_one_file": self.output_in_one_file.get(),
            "geometry": self.geometry()
        }
        with open("../ui_status.json", "w") as file:
            json.dump(ui_status, file)

    def on_closing(self):
        self.save_ui_status()
        self.destroy()

    def _on_epub_file_path_change(self, *args):
        # Call the function to load epub file chapters

        self.load_epub_file_chapters()

    def _delete_chapter_list(self):
        if self.chapter_listbox.size() > 0:

            self._log("Deleting chapter list...")

            self.chapter_text_by_filename = {}
            for i in range(self.chapter_listbox.size(), -1, -1):
                self.chapter_listbox.delete(i)
                self.main_frame.update()

    def _fill_chapter_list(self, chapters_filename_and_text):

        self._log("filling chapter list...")

        for file_name, text in chapters_filename_and_text:
            self.chapter_text_by_filename[file_name] = text
            self.chapter_listbox.insert(tk.END, file_name)

    def load_epub_file_chapters(self):

        epub_file_path = self.epub_file_path.get()

        if file_management.file_exists(epub_file_path):
            self._delete_chapter_list()

            self._log(f"Loading {epub_file_path} ...")

            self.output_file_name.set(file_management.extract_file_name(epub_file_path))

            title, chapters_filename_and_text = epub_reader.get_title_and_chapters(epub_file_path)

            self.book_title.set(title)
            self._fill_chapter_list(chapters_filename_and_text)

            self._log(f"Loaded.")

    def _select_all_chapters(self):
        self.chapter_listbox.command = None
        self.update_idletasks()

        for i in range(self.chapter_listbox.size()):
            self.chapter_listbox.activate(i)

            self._log(f"Selecting {i}...")

            self.main_frame.update()

            self.update_idletasks()

        self.chapter_listbox.command = self._display_selected_chapter_text
        self.update_idletasks()

        self._log(f"Selection done.")

    def _unselect_all_chapters(self):
        for i in range(self.chapter_listbox.size()):
            self.chapter_listbox.deactivate(i)


if __name__ == "__main__":
    app = EpubAudioConverterUI()
    app.mainloop()
