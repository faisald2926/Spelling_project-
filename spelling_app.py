import tkinter as tk
from tkinter import ttk, messagebox, StringVar, filedialog, font
import pyttsx3
import threading
import time
import json
import os
import random

try:
    from word_lists import WordListManager
except ImportError:
    messagebox.showerror("Error", "Could not find word_lists.py. Make sure it's in the same directory.")
    exit()


class SpellingApp:
    # --- Constants ---
    BG_COLOR = "#2E2E2E"
    FG_COLOR = "white"
    INPUT_BG_COLOR = "#3E3E3E"
    BUTTON_BG_COLOR = "#4A4A4A"
    BUTTON_ACTIVE_BG_COLOR = "#5E5E5E"
    CORRECT_COLOR = "#4CAF50" # Green
    INCORRECT_COLOR = "#F44336" # Red
    HINT_COLOR = "#2196F3" # Blue

    DEFAULT_FONT_FAMILY = "Arial"
    MIN_FONT_SIZE = 8
    MAX_FONT_SIZE = 24

    def __init__(self, root):
        self.root = root
        self.root.title("Spelling Practice App")
        self.root.geometry("850x700")
        self.root.configure(bg=self.BG_COLOR)
        self.root.minsize(700, 550)

        self.base_font_size = 12
        self.update_fonts()
        self.style = ttk.Style() # Initialize style object early
        self.configure_styles()

        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
        except Exception as e:
            self.engine = None
            print(f"TTS Initialization Warning: {e}")
            messagebox.showwarning("TTS Warning", f"Text-to-speech engine failed.\nError: {e}\nPlayback disabled.")

        self.word_manager = WordListManager()
        self.misspelled_words = []
        self.misspelled_tracking = {}
        self.current_word_index = -1
        self.practicing_misspelled = False
        self.presented_indices = set()

        self._create_widgets()
        self._initial_setup()


    def _create_widgets(self):
        """Creates and grids all the GUI elements."""
        self.main_frame = ttk.Frame(self.root, padding="20", style='TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.main_frame.rowconfigure(6, weight=1)
        self.main_frame.columnconfigure(0, weight=1)

        # --- Header & Font ---
        header_frame = ttk.Frame(self.main_frame, style='TFrame')
        header_frame.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky="ew")
        header_frame.columnconfigure(1, weight=1)
        self.header_label = ttk.Label(header_frame, text="Spelling Practice", font=self.header_font, anchor="center", style='TLabel')
        self.header_label.grid(row=0, column=1, sticky="ew")
        self.font_decrease_button = ttk.Button(header_frame, text="A-", command=self.decrease_font_size, width=3, style='TButton')
        self.font_decrease_button.grid(row=0, column=0, sticky="w", padx=5)
        self.font_increase_button = ttk.Button(header_frame, text="A+", command=self.increase_font_size, width=3, style='TButton')
        self.font_increase_button.grid(row=0, column=2, sticky="e", padx=5)

        # --- List Selection ---
        list_frame = ttk.Frame(self.main_frame, style='TFrame')
        list_frame.grid(row=1, column=0, columnspan=3, pady=10, sticky="ew")
        list_frame.columnconfigure(1, weight=1)
        self.list_label = ttk.Label(list_frame, text="Word List:", font=self.normal_font, style='TLabel')
        self.list_label.grid(row=0, column=0, padx=(0, 5), sticky="w")
        self.word_list_var = StringVar()
        available_lists = self.word_manager.get_available_lists()
        self.word_list_dropdown = ttk.Combobox(list_frame, textvariable=self.word_list_var, values=available_lists, state="readonly", style='TCombobox')
        self.word_list_dropdown.grid(row=0, column=1, padx=5, sticky="ew")
        if available_lists:
            default_list = self.word_manager.get_active_list_name()
            if default_list in available_lists: self.word_list_dropdown.set(default_list)
            else: self.word_list_dropdown.current(0)
        self.word_list_dropdown.bind("<<ComboboxSelected>>", self.change_word_list)

        # --- Word Interaction ---
        interaction_frame = ttk.Frame(self.main_frame, style='TFrame')
        interaction_frame.grid(row=2, column=0, columnspan=3, pady=20, sticky="ew")
        interaction_frame.columnconfigure(1, weight=1)
        self.play_button = ttk.Button(interaction_frame, text="🔊 Play Word", command=self.play_word, style='TButton')
        self.play_button.grid(row=0, column=0, padx=(0,10))
        if not self.engine: self.play_button.config(state=tk.DISABLED)
        self.user_input = ttk.Entry(interaction_frame, font=self.entry_font, style='TEntry')
        self.user_input.grid(row=0, column=1, sticky="ew", ipady=5)
        self.user_input.bind("<Return>", lambda event: self.check_spelling())
        self.user_input.bind("<space>", lambda event: self.check_spelling())
        self.submit_button = ttk.Button(interaction_frame, text="Submit (Spc)", command=self.check_spelling, style='TButton')
        self.submit_button.grid(row=0, column=2, padx=(10, 5))
        self.hint_button = ttk.Button(interaction_frame, text="Hint", command=self.show_hint, style='TButton')
        self.hint_button.grid(row=0, column=3, padx=(0, 0))

        # --- Feedback & Progress ---
        self.feedback_label = ttk.Label(self.main_frame, text="Select a list to begin.", font=self.feedback_font, anchor="center", style='TLabel')
        self.feedback_label.grid(row=3, column=0, columnspan=3, pady=10, sticky="ew")
        self.progress_label = ttk.Label(self.main_frame, text="", font=self.small_font, anchor="center", style='TLabel')
        self.progress_label.grid(row=4, column=0, columnspan=3, pady=5, sticky="ew")

        # --- Action Buttons ---
        action_button_frame = ttk.Frame(self.main_frame, style='TFrame')
        action_button_frame.grid(row=5, column=0, columnspan=3, pady=10, sticky="ew")
        action_button_frame.columnconfigure(0, weight=1)
        action_button_frame.columnconfigure(1, weight=1)
        action_button_frame.columnconfigure(2, weight=1)
        self.save_button = ttk.Button(action_button_frame, text="Save Misspelled", command=self.save_misspelled_words, style='TButton')
        self.save_button.grid(row=0, column=0, padx=5, sticky="ew")
        self.load_button = ttk.Button(action_button_frame, text="Load Misspelled", command=self.load_misspelled_words, style='TButton')
        self.load_button.grid(row=0, column=1, padx=5, sticky="ew")
        self.practice_button = ttk.Button(action_button_frame, text="Practice Misspelled", command=self.practice_misspelled_words, style='TButton')
        self.practice_button.grid(row=0, column=2, padx=5, sticky="ew")

        # --- Misspelled Log ---
        misspelled_frame = ttk.Frame(self.main_frame, style='TFrame')
        misspelled_frame.grid(row=6, column=0, columnspan=3, pady=(10, 0), sticky="nsew")
        misspelled_frame.rowconfigure(1, weight=1)
        misspelled_frame.columnconfigure(0, weight=1)
        self.misspelled_label = ttk.Label(misspelled_frame, text="Misspelled Words Log:", font=self.normal_bold_font, style='TLabel')
        self.misspelled_label.grid(row=0, column=0, sticky="w")
        self.misspelled_list = tk.Text(misspelled_frame, height=6, bg=self.INPUT_BG_COLOR, fg=self.FG_COLOR, font=self.small_font, borderwidth=1, relief=tk.SUNKEN, wrap=tk.WORD)
        self.misspelled_list.grid(row=1, column=0, sticky="nsew")
        self.misspelled_list.config(state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(misspelled_frame, orient=tk.VERTICAL, command=self.misspelled_list.yview, style='TScrollbar')
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.misspelled_list['yscrollcommand'] = scrollbar.set

    def _initial_setup(self):
        """Sets initial focus and loads the first word if lists exist."""
        self.user_input.focus_set()
        self.update_widget_fonts() # Apply fonts after widgets created

        if self.word_manager.get_available_lists():
            self.root.after(100, lambda: self.change_word_list(event=None))
        else:
            self.feedback_label.config(text="No word lists found.", foreground=self.INCORRECT_COLOR)

    def update_fonts(self):
        """Updates font objects based on base_font_size."""
        self.header_font = font.Font(family=self.DEFAULT_FONT_FAMILY, size=int(self.base_font_size * 1.8), weight="bold")
        self.normal_font = font.Font(family=self.DEFAULT_FONT_FAMILY, size=self.base_font_size)
        self.normal_bold_font = font.Font(family=self.DEFAULT_FONT_FAMILY, size=self.base_font_size, weight="bold")
        self.entry_font = font.Font(family=self.DEFAULT_FONT_FAMILY, size=int(self.base_font_size * 1.1))
        self.feedback_font = font.Font(family=self.DEFAULT_FONT_FAMILY, size=int(self.base_font_size * 1.1))
        self.small_font = font.Font(family=self.DEFAULT_FONT_FAMILY, size=int(self.base_font_size * 0.9))
        self.button_font = font.Font(family=self.DEFAULT_FONT_FAMILY, size=self.base_font_size)

    def update_widget_fonts(self):
        """Applies the current font objects to relevant widgets."""
        self.misspelled_list.config(font=self.small_font)
        self.style.configure('TButton', font=self.button_font)
        self.style.configure('TLabel', font=self.normal_font)
        self.style.configure('TEntry', font=self.entry_font)
        self.style.configure('TCombobox', font=self.normal_font)
        self.header_label.config(font=self.header_font)
        self.list_label.config(font=self.normal_font)
        self.feedback_label.config(font=self.feedback_font)
        self.progress_label.config(font=self.small_font)
        self.misspelled_label.config(font=self.normal_bold_font)
        self.root.update_idletasks()

    def increase_font_size(self):
        """Increases the base font size."""
        if self.base_font_size < self.MAX_FONT_SIZE:
            self.base_font_size += 1
            self.update_fonts()
            self.update_widget_fonts()

    def decrease_font_size(self):
        """Decreases the base font size."""
        if self.base_font_size > self.MIN_FONT_SIZE:
            self.base_font_size -= 1
            self.update_fonts()
            self.update_widget_fonts()

    def configure_styles(self):
        """Configures ttk styles for the dark theme."""
        self.style.theme_use('clam')
        self.style.configure('.', background=self.BG_COLOR, foreground=self.FG_COLOR, font=self.normal_font)
        self.style.configure('TFrame', background=self.BG_COLOR)
        self.style.configure('TLabel', background=self.BG_COLOR, foreground=self.FG_COLOR)
        self.style.configure('TButton', background=self.BUTTON_BG_COLOR, foreground=self.FG_COLOR, font = self.button_font, borderwidth=1, relief=tk.RAISED, padding=(10, 5), anchor=tk.CENTER)
        self.style.map('TButton', background=[('active', self.BUTTON_ACTIVE_BG_COLOR), ('pressed', self.BUTTON_ACTIVE_BG_COLOR), ('disabled', '#555')], foreground=[('disabled', '#999')], relief=[('pressed', tk.SUNKEN), ('!pressed', tk.RAISED)])
        self.style.configure('TEntry', fieldbackground=self.INPUT_BG_COLOR, foreground=self.FG_COLOR, insertcolor=self.FG_COLOR, borderwidth=1, relief=tk.SUNKEN, padding=(5, 5))
        self.root.option_add('*TCombobox*Listbox.background', self.INPUT_BG_COLOR)
        self.root.option_add('*TCombobox*Listbox.foreground', self.FG_COLOR)
        self.root.option_add('*TCombobox*Listbox.selectBackground', self.BUTTON_ACTIVE_BG_COLOR)
        self.root.option_add('*TCombobox*Listbox.selectForeground', self.FG_COLOR)
        self.style.configure('TCombobox', fieldbackground=self.INPUT_BG_COLOR, background=self.BUTTON_BG_COLOR, foreground=self.FG_COLOR, arrowcolor=self.FG_COLOR, insertcolor=self.FG_COLOR, padding=(5,5), borderwidth=1, relief=tk.FLAT)
        self.style.map('TCombobox', fieldbackground=[('readonly', self.INPUT_BG_COLOR), ('disabled', '#444')], foreground=[('disabled', '#999')], background=[('readonly', self.BUTTON_BG_COLOR), ('disabled', '#555')], arrowcolor=[('disabled', '#777')])
        self.style.configure('TScrollbar', background=self.BUTTON_BG_COLOR, troughcolor=self.INPUT_BG_COLOR, borderwidth=0, arrowcolor=self.FG_COLOR, relief=tk.FLAT)
        self.style.map('TScrollbar', background=[('active', self.BUTTON_ACTIVE_BG_COLOR), ('!active', self.BUTTON_BG_COLOR)], relief=[('active', tk.RAISED), ('!active', tk.FLAT)])

    # --- Word Playback ---
    def schedule_double_play(self):
        """Plays the current word twice with a delay, using threads."""
        if not self.engine or self.play_button['state'] == tk.DISABLED: return
        current_word = self.get_current_word()
        if not current_word: return

        self.play_button.config(state=tk.DISABLED)
        thread1 = threading.Thread(target=self._speak_word_and_schedule_next, args=(current_word,), daemon=True)
        thread1.start()

    def _speak_word_and_schedule_next(self, word_to_speak):
        """TTS helper: Speaks once, schedules second play."""
        try:
            self.engine.say(word_to_speak)
            self.engine.runAndWait()
            self.root.after(1000, lambda: self._schedule_second_play(word_to_speak))
        except Exception as e:
            print(f"TTS Error (1st play): {e}")
            self.root.after(0, self._enable_play_button)

    def _schedule_second_play(self, word_to_speak):
        """TTS helper: Schedules the second speak in a thread."""
        if not self.engine:
             self._enable_play_button()
             return
        thread2 = threading.Thread(target=self._speak_second_time, args=(word_to_speak,), daemon=True)
        thread2.start()

    def _speak_second_time(self, word_to_speak):
        """TTS helper: Speaks second time, re-enables button."""
        try:
             self.engine.say(word_to_speak)
             self.engine.runAndWait()
        except Exception as e:
             print(f"TTS Error (2nd play): {e}")
        finally:
            self.root.after(0, self._enable_play_button)

    def _enable_play_button(self):
        """Safely enables the play button."""
        if self.engine:
            try: self.play_button.config(state=tk.NORMAL)
            except tk.TclError: pass # Ignore if window closing

    # --- Word/List Management ---
    def _select_next_random_word(self):
        """Selects a random, unpresented word from the current list."""
        word_list = self.misspelled_words if self.practicing_misspelled else self.word_manager.get_active_list()
        total_words = len(word_list)
        if total_words == 0:
            self.current_word_index = -1
            self.update_progress_label()
            self.feedback_label.config(text="List is empty.", foreground=self.FG_COLOR)
            return False

        available_indices = [i for i in range(total_words) if i not in self.presented_indices]
        if not available_indices:
            self.current_word_index = -1
            self.update_progress_label()
            return False # List finished

        self.current_word_index = random.choice(available_indices)
        self.presented_indices.add(self.current_word_index)
        self.update_progress_label()
        self.feedback_label.config(text="") # Clear previous feedback
        return True

    def change_word_list(self, event=None):
        """Handles changing the word list via dropdown or initial load."""
        selected_list = self.word_list_var.get()
        if not selected_list:
             available = self.word_manager.get_available_lists()
             if available:
                 selected_list = available[0]
                 self.word_list_var.set(selected_list)
             else:
                 self.feedback_label.config(text="No word lists available.", foreground=self.INCORRECT_COLOR)
                 self.reset_practice_state()
                 self.update_progress_label()
                 return

        if self.word_manager.set_active_list(selected_list):
            self.reset_practice_state()
            if self._select_next_random_word():
                self.schedule_double_play()
                self.feedback_label.config(text=f"Switched to '{selected_list}'. Listen...", foreground=self.FG_COLOR)
            else:
                self.feedback_label.config(text=f"Switched to '{selected_list}' (List is empty).", foreground=self.INCORRECT_COLOR)
                self.update_progress_label()
            self.misspelled_words = []
            self.misspelled_tracking = {}
            self.update_misspelled_list_display()
        else:
            messagebox.showerror("Error", f"Could not switch to list: {selected_list}")
        self.user_input.focus_set()

    def reset_practice_state(self):
        """Resets state variables for a new practice session or list change."""
        self.current_word_index = -1
        self.practicing_misspelled = False
        self.presented_indices.clear()
        try:
            self.user_input.delete(0, tk.END)
            self.user_input.focus_set()
        except tk.TclError: pass

    def get_current_word(self):
        """Safely gets the current word based on index and mode."""
        if self.current_word_index == -1: return None
        word_list = self.misspelled_words if self.practicing_misspelled else self.word_manager.get_active_list()
        if word_list and 0 <= self.current_word_index < len(word_list):
            return word_list[self.current_word_index]
        else:
            self.current_word_index = -1 # Invalid state
            return None

    def play_word(self):
        """Plays the current word (triggered by button)."""
        if not self.engine:
             self.feedback_label.config(text="TTS engine not available.", foreground=self.INCORRECT_COLOR)
             if not self.engine: self.play_button.config(state=tk.DISABLED)
             return
        current_word = self.get_current_word()
        if current_word:
            self.schedule_double_play()
        else:
            self.feedback_label.config(text="No spelling word selected yet.", foreground=self.INCORRECT_COLOR)
            self._enable_play_button()

    # --- Spelling Check & Progression ---
    def check_spelling(self):
        """Checks the user's input against the correct spelling."""
        current_word = self.get_current_word()
        if not current_word:
            self.feedback_label.config(text="No spelling word to check.", foreground=self.INCORRECT_COLOR)
            return

        user_spelling = self.user_input.get().strip()
        correct_spelling = current_word
        is_correct = (user_spelling.lower() == correct_spelling.lower())

        if is_correct:
            self.feedback_label.config(text="Correct! ✓", foreground=self.CORRECT_COLOR)
            if correct_spelling in self.misspelled_tracking:
                 self.misspelled_tracking[correct_spelling]['correct_attempts'] = self.misspelled_tracking[correct_spelling].get('correct_attempts', 0) + 1
                 self.update_misspelled_list_display()
        else:
            self.feedback_label.config(text=f"Incorrect! Correct: '{correct_spelling}'", foreground=self.INCORRECT_COLOR)
            if correct_spelling not in self.misspelled_words:
                 self.misspelled_words.append(correct_spelling)
            if correct_spelling not in self.misspelled_tracking:
                self.misspelled_tracking[correct_spelling] = {'incorrect_attempts': 0, 'correct_attempts': 0, 'user_attempts': []}

            tracking_entry = self.misspelled_tracking[correct_spelling]
            tracking_entry['incorrect_attempts'] = tracking_entry.get('incorrect_attempts', 0) + 1
            attempt = user_spelling if user_spelling else "(empty)"
            if attempt not in tracking_entry.get('user_attempts', []):
                tracking_entry['user_attempts'] = tracking_entry.get('user_attempts', [])[-4:] + [attempt] # Keep last 5 attempts

            self.update_misspelled_list_display()

        self.user_input.delete(0, tk.END)
        self.root.after(1500, self.next_word)

    def next_word(self):
        """Moves to the next word or shows results if finished."""
        word_selected = self._select_next_random_word()
        if word_selected:
            self.schedule_double_play()
            self.user_input.focus_set()
        else:
            if self.practicing_misspelled: self.show_practice_results()
            else: self.show_results()

    def update_progress_label(self):
        """Updates the label showing current progress."""
        word_list = self.misspelled_words if self.practicing_misspelled else self.word_manager.get_active_list()
        word_list = word_list if isinstance(word_list, list) else []
        total_words = len(word_list)
        presented_count = len(self.presented_indices)
        list_name = self.word_manager.get_active_list_name()
        mode = "Practicing Misspelled" if self.practicing_misspelled else f"List: '{list_name}'" if list_name else "List: (None)"

        progress_text = f"{mode} - "
        if total_words == 0:
             progress_text += "List is empty" if list_name else "No list selected"
        elif presented_count >= total_words:
             progress_text += f"Completed ({total_words}/{total_words})"
        elif self.current_word_index == -1 and presented_count == 0:
             progress_text += f"0/{total_words} (Ready)"
        else:
            progress_text += f"Word {presented_count}/{total_words}"
        try: self.progress_label.config(text=progress_text)
        except tk.TclError: pass

    def show_results(self):
        """Displays results after finishing a regular list."""
        active_list_name = self.word_manager.get_active_list_name()
        active_list = self.word_manager.get_active_list()
        total_words = len(active_list) if isinstance(active_list, list) else 0

        if total_words == 0:
            messagebox.showinfo("Practice Complete", f"The list '{active_list_name}' is empty.")
        else:
            session_misspelled_count = len([w for w in self.misspelled_words if w in active_list])
            messagebox.showinfo("Practice Complete", f"Finished '{active_list_name}' list!\n\nTotal Words: {total_words}\nMisspelled this session: {session_misspelled_count}")

        self.reset_practice_state()
        self.update_progress_label()
        self.feedback_label.config(text="Practice complete. Choose list or practice.", foreground=self.FG_COLOR)
        self.user_input.focus_set()

    def show_practice_results(self):
        """Displays results after practicing misspelled words."""
        practiced_words = list(self.misspelled_tracking.keys())
        total_practiced = len(practiced_words)
        if total_practiced == 0:
             messagebox.showinfo("Practice Complete", "No misspelled words were practiced.")
        else:
            correct_this_round = sum(1 for word in practiced_words if self.misspelled_tracking[word].get('correct_attempts', 0) > 0)
            messagebox.showinfo("Practice Complete", f"Finished practicing {total_practiced} words!\nCorrect this round: {correct_this_round}/{total_practiced}")

        self.switch_to_regular_mode()
        self.feedback_label.config(text="Misspelled practice complete.", foreground=self.FG_COLOR)

    def switch_to_regular_mode(self):
        """Switches back to regular mode after practice or load."""
        self.practicing_misspelled = False
        self.reset_practice_state()
        current_dropdown_list = self.word_list_var.get()
        if self.word_manager.set_active_list(current_dropdown_list):
             if self._select_next_random_word():
                 self.schedule_double_play()
                 self.feedback_label.config(text=f"Resumed list '{current_dropdown_list}'. Listen...", fg=self.FG_COLOR)
             else:
                 self.feedback_label.config(text=f"Resumed list '{current_dropdown_list}' (Empty).", fg=self.INCORRECT_COLOR)
             self.update_progress_label()
        else:
             self.feedback_label.config(text="Select a word list.", fg=self.FG_COLOR)
             self.update_progress_label()
        self.user_input.focus_set()

    # --- Misspelled Log & Persistence ---
    def update_misspelled_list_display(self):
        """Updates the text area showing misspelled words and stats."""
        try:
            last_pos = self.misspelled_list.yview()
            self.misspelled_list.config(state=tk.NORMAL)
            self.misspelled_list.delete(1.0, tk.END)
            if not self.misspelled_words:
                self.misspelled_list.insert(tk.END, "No words misspelled yet.")
            else:
                lines = []
                for word in self.misspelled_words:
                    info = self.misspelled_tracking.get(word, {})
                    inc = info.get('incorrect_attempts', 0)
                    cor = info.get('correct_attempts', 0)
                    atts = info.get('user_attempts', [])[-3:] # Last 3 attempts
                    entry = f"• {word} (Inc: {inc}, Cor: {cor})"
                    if atts: entry += f"\n   Attempts: {', '.join([f'{a}' for a in atts])}"
                    lines.append(entry)
                self.misspelled_list.insert(tk.END, "\n".join(lines))
            self.misspelled_list.config(state=tk.DISABLED)
            self.misspelled_list.yview_moveto(last_pos[0])
        except Exception as e: print(f"Error updating misspelled list: {e}")

    def save_misspelled_words(self):
        """Saves current misspelled words and tracking to JSON."""
        if not self.misspelled_words:
            messagebox.showwarning("No Data", "No misspelled words to save.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Log", "*.json"), ("All", "*.*")], title="Save Misspelled Log")
        if not file_path: return
        data_to_save = {'saved_misspelled_words': self.misspelled_words, 'saved_tracking_data': self.misspelled_tracking}
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Success", f"Log saved to:\n{file_path}")
        except Exception as e: messagebox.showerror("Save Error", f"Failed to save:\n{e}")

    def load_misspelled_words(self):
        """Loads misspelled words and tracking from JSON."""
        file_path = filedialog.askopenfilename(filetypes=[("JSON Log", "*.json"), ("All", "*.*")], title="Load Misspelled Log")
        if not file_path: return
        try:
            with open(file_path, 'r', encoding='utf-8') as f: loaded_data = json.load(f)
            if not isinstance(loaded_data, dict): raise ValueError("Invalid format.")
            words = loaded_data.get('saved_misspelled_words')
            tracking = loaded_data.get('saved_tracking_data')
            if not isinstance(words, list) or not isinstance(tracking, dict): raise ValueError("Invalid data types.")

            self.misspelled_words = []
            self.misspelled_tracking = {}
            loaded_count, skipped_count = 0, 0
            for word in words:
                 if isinstance(word, str) and word:
                     self.misspelled_words.append(word)
                     loaded_count += 1
                     word_tracking = tracking.get(word, {})
                     self.misspelled_tracking[word] = {
                         'incorrect_attempts': word_tracking.get('incorrect_attempts', 0),
                         'correct_attempts': word_tracking.get('correct_attempts', 0),
                         'user_attempts': word_tracking.get('user_attempts', []) }
                 else: skipped_count += 1

            self.update_misspelled_list_display()
            info_msg = f"Loaded {loaded_count} words." + (f" Skipped {skipped_count} invalid." if skipped_count else "")
            messagebox.showinfo("Load Successful", info_msg)

            if self.misspelled_words:
                 if messagebox.askyesno("Practice Loaded?", "Practice these words now?"):
                     self.practice_misspelled_words()
                 else:
                     self.feedback_label.config(text="Loaded words ready for practice.", fg=self.FG_COLOR)
                     self.update_progress_label()
            else:
                 messagebox.showinfo("Info", "Loaded file empty or invalid.")
                 self.switch_to_regular_mode()
        except Exception as e: messagebox.showerror("Load Error", f"{e}")

    def practice_misspelled_words(self):
        """Initiates practice mode for the current misspelled words."""
        if not self.misspelled_words:
            messagebox.showinfo("No Data", "No misspelled words to practice.")
            return
        self.practicing_misspelled = True
        self.current_word_index = -1
        self.presented_indices.clear()
        for word in self.misspelled_tracking: # Reset counts for this round
            self.misspelled_tracking[word]['correct_attempts'] = 0

        if self._select_next_random_word():
             self.schedule_double_play()
             self.feedback_label.config(text="Practicing misspelled words...", fg=self.FG_COLOR)
             self.update_progress_label()
        else:
            self.feedback_label.config(text="Error starting practice.", fg=self.INCORRECT_COLOR)
            self.switch_to_regular_mode()
        self.user_input.delete(0, tk.END)
        self.user_input.focus_set()

    # --- Hint Feature ---
    def show_hint(self):
        """Displays a contextual hint for the current word."""
        current_word = self.get_current_word()
        if not current_word:
            self.feedback_label.config(text="No word active for hint.", fg=self.INCORRECT_COLOR)
            return

        hints = []
        w_lower = current_word.lower()
        has_double = any(w_lower[i] == w_lower[i+1] and w_lower[i].isalpha() for i in range(len(w_lower)-1))
        if has_double: hints.append("Watch for double letters.")
        if 'ie' in w_lower or 'ei' in w_lower: hints.append("Check the 'i' before 'e' rule.")
        sfx = {"tion":"sion", "able":"ible", "ance":"ence", "ary":"ery", "ify":"efy"}
        for s1, s2 in sfx.items():
            if w_lower.endswith(s1) or w_lower.endswith(s2):
                hints.append(f"Ending: '-{s1}' or '-{s2}'?")
                break
        if not hints: hints.append(f"{len(current_word)} letters.")
        if len(hints) < 2 and len(w_lower) > 1: hints.append(f"Starts '{current_word[0]}', ends '{current_word[-1]}'.")
        if not hints:
             generic = ["Silent letters?", "Homophones?", "Syllables?", "Root/Prefix/Suffix?"]
             hints.append(f"Tip: {random.choice(generic)}")

        if hints: self.feedback_label.config(text=f"Hint: {random.choice(hints)}", fg=self.HINT_COLOR)
        else: self.feedback_label.config(text="Hint unavailable.", fg=self.HINT_COLOR)
        self.user_input.focus_set()


if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg=SpellingApp.BG_COLOR) # Set root BG early
    app = SpellingApp(root)
    root.mainloop()
