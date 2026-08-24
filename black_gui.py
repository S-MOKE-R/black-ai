#!/usr/bin/env python3
"""
Black AI - Bug Bounty Assistant
Developer: @S_MOKE_R
GitHub: https://github.com/S-MOKE-R
Telegram: https://t.me/S_MOKE_R
Channel: https://t.me/VOID_SMOKER
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import os
import json
import sqlite3
import re
import webbrowser
from datetime import datetime

CONFIG_FILE = os.path.expanduser("~/.black_config.json")

class BlackGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🔒 Black - Bug Bounty Assistant")
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width = int(screen_width * 0.92)
        height = int(screen_height * 0.88)
        x = int((screen_width - width) / 2)
        y = int((screen_height - height) / 2)
        
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.minsize(1000, 650)
        self.root.configure(bg='#0a0a0a')
        
        # Load config
        self.config = self.load_config()
        self.api_key = self.config.get("api_key", "")
        self.user_name = self.config.get("user_name", "hacker")
        self.mode = self.config.get("mode", "normal")
        
        # Database
        self.db_file = os.path.expanduser("~/black/black_interactions.db")
        self.history_file = os.path.expanduser("~/black/black_history.json")
        self.setup_database()
        self.history = self.load_history()
        self.last_question = None
        self.last_answer = None
        
        # Colors
        self.colors = {
            'bg': '#0a0a0a',
            'bg2': '#111111',
            'bg3': '#1a1a1a',
            'bg4': '#222222',
            'fg': '#00ff41',
            'fg2': '#00cc33',
            'accent': '#00ff41',
            'danger': '#ff0040',
            'warning': '#ffaa00',
            'user_bubble': '#0a1a0a',
            'ai_bubble': '#0a0a1a',
            'terminal': '#000000',
            'terminal_fg': '#00ff41',
            'terminal_bg': '#000000',
            'border': '#003300'
        }
        
        self.black_script = os.path.expanduser("~/black/black.sh")
        self.setup_ui()
        self.setup_shortcuts()
        
        if not self.api_key:
            self.show_settings()
            self.add_message("system", "⚡ Please set your API key in Settings.")
        else:
            self.add_message("system", "⚡ Black initialized. Welcome, {}!".format(self.user_name))
            self.add_message("assistant", "I'm your bug bounty hunting AI. Type 'scan target.com' to start.")
            self.add_message("assistant", "Black by @S_MOKE_R | Open Source")
        
        self.add_terminal("🔒 Black Terminal Ready")
        
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)

    def setup_database(self):
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS interactions
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      question TEXT NOT NULL,
                      answer TEXT NOT NULL,
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
        conn.close()

    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_history(self):
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)

    def add_interaction(self, question, answer):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("INSERT INTO interactions (question, answer) VALUES (?, ?)", (question, answer))
        conn.commit()
        conn.close()
        self.history.append({"question": question, "answer": answer})
        self.save_history()
        self.last_question = question
        self.last_answer = answer

    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Header
        header = tk.Frame(main_frame, bg=self.colors['bg2'], height=45)
        header.pack(fill=tk.X, pady=(0, 8))
        header.pack_propagate(False)
        
        left = tk.Frame(header, bg=self.colors['bg2'])
        left.pack(side=tk.LEFT, padx=15, fill=tk.Y)
        
        tk.Label(left, text="🔒", font=("Courier New", 18),
                bg=self.colors['bg2'], fg=self.colors['fg']).pack(side=tk.LEFT, padx=(0, 8))
        
        tk.Label(left, text="BLACK", font=("Courier New", 14, "bold"),
                fg=self.colors['fg'], bg=self.colors['bg2']).pack(side=tk.LEFT)
        
        tk.Label(left, text="BUG BOUNTY", font=("Courier New", 8),
                fg=self.colors['fg2'], bg=self.colors['bg2']).pack(side=tk.LEFT, padx=(5, 0))
        
        self.history_label = tk.Label(left, text="📜 0", font=("Courier New", 8),
                                      fg=self.colors['fg2'], bg=self.colors['bg2'])
        self.history_label.pack(side=tk.LEFT, padx=10)
        
        right = tk.Frame(header, bg=self.colors['bg2'])
        right.pack(side=tk.RIGHT, padx=15)
        
        # Mode label
        mode_text = "🔓 NORMAL" if self.mode == "normal" else "⚡ FULL"
        self.mode_label = tk.Label(right, text=mode_text, font=("Courier New", 8, "bold"),
                                   fg=self.colors['fg2'], bg=self.colors['bg2'])
        self.mode_label.pack(side=tk.LEFT, padx=10)
        
        # Settings button - ALWAYS VISIBLE
        settings_btn = tk.Button(right, text="⚙️ Settings", command=self.show_settings,
                                 font=("Courier New", 9, "bold"),
                                 bg=self.colors['bg3'], fg=self.colors['fg'],
                                 relief=tk.FLAT, padx=10, pady=4,
                                 cursor='hand2')
        settings_btn.pack(side=tk.LEFT, padx=5)
        
        self.status_dot = tk.Canvas(right, width=10, height=10, bg=self.colors['bg2'], highlightthickness=0)
        self.status_dot.pack(side=tk.LEFT, padx=(0, 8))
        self.status_dot.create_oval(2, 2, 8, 8, fill=self.colors['accent'], tags="dot")
        
        self.status_label = tk.Label(right, text="READY", font=("Courier New", 9, "bold"),
                                     fg=self.colors['fg2'], bg=self.colors['bg2'])
        self.status_label.pack(side=tk.LEFT)
        
        divider = tk.Frame(main_frame, bg=self.colors['border'], height=1)
        divider.pack(fill=tk.X, pady=4)
        
        # Split View
        paned = tk.PanedWindow(main_frame, orient=tk.HORIZONTAL,
                               bg=self.colors['bg'], sashrelief=tk.FLAT, sashwidth=4)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Chat Panel
        chat_panel = tk.Frame(paned, bg=self.colors['bg'])
        paned.add(chat_panel, width=700)
        
        chat_container = tk.Frame(chat_panel, bg=self.colors['bg'])
        chat_container.pack(fill=tk.BOTH, expand=True, pady=(0, 6))
        
        self.chat_canvas = tk.Canvas(chat_container, bg=self.colors['bg'], highlightthickness=0)
        chat_scrollbar = ttk.Scrollbar(chat_container, orient="vertical", command=self.chat_canvas.yview)
        self.chat_canvas.configure(yscrollcommand=chat_scrollbar.set)
        
        chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.messages_frame = tk.Frame(self.chat_canvas, bg=self.colors['bg'])
        self.chat_canvas.create_window((0, 0), window=self.messages_frame, anchor="nw")
        self.messages_frame.bind("<Configure>", lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all")))
        self.chat_canvas.bind("<Configure>", lambda e: self.chat_canvas.itemconfig(1, width=e.width))
        
        # Chat input
        input_container = tk.Frame(chat_panel, bg=self.colors['bg'])
        input_container.pack(fill=tk.X)
        
        input_frame = tk.Frame(input_container, bg=self.colors['bg2'], relief=tk.FLAT, bd=1)
        input_frame.pack(fill=tk.X)
        
        self.input_entry = tk.Text(input_frame, font=("Courier New", 10),
                                   bg=self.colors['bg2'], fg=self.colors['fg'],
                                   height=1, wrap=tk.WORD,
                                   relief=tk.FLAT,
                                   insertbackground=self.colors['fg'],
                                   padx=8, pady=4)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_entry.bind('<Return>', self.handle_enter)
        
        self.send_btn = tk.Button(input_frame, text="▶ SEND",
                                  command=self.send_message,
                                  font=("Courier New", 9, "bold"),
                                  bg=self.colors['bg3'], fg=self.colors['fg'],
                                  relief=tk.FLAT,
                                  padx=15, pady=4,
                                  cursor='hand2')
        self.send_btn.pack(side=tk.RIGHT, padx=5, pady=4)
        
        # Quick actions
        quick_frame = tk.Frame(chat_panel, bg=self.colors['bg'])
        quick_frame.pack(fill=tk.X, pady=(4, 0))
        
        quick_buttons = [
            ("📜 HISTORY", "history"),
            ("🔍 SEARCH", "search"),
            ("📂 FILES", "ls -la ~/Downloads"),
            ("🔄 CLEAR", "clear"),
            ("💀 MENU", "menu"),
            ("⚡ SCAN", "scan")
        ]
        
        for text, cmd in quick_buttons:
            btn = tk.Button(quick_frame, text=text,
                          command=lambda c=cmd: self.quick_action(c),
                          font=("Courier New", 8, "bold"),
                          bg=self.colors['bg2'], fg=self.colors['fg2'],
                          relief=tk.FLAT, padx=8, pady=2,
                          cursor='hand2',
                          activebackground=self.colors['bg3'])
            btn.pack(side=tk.LEFT, padx=2)
        
        # Terminal Panel
        terminal_panel = tk.Frame(paned, bg=self.colors['bg'])
        paned.add(terminal_panel, width=400)
        
        term_header = tk.Frame(terminal_panel, bg=self.colors['bg2'], height=28)
        term_header.pack(fill=tk.X, pady=(0, 4))
        term_header.pack_propagate(False)
        
        tk.Label(term_header, text="💻 TERMINAL", font=("Courier New", 9, "bold"),
                fg=self.colors['fg'], bg=self.colors['bg2']).pack(side=tk.LEFT, padx=10)
        
        self.terminal_text = tk.Text(terminal_panel,
                                     font=("Courier New", 9),
                                     bg=self.colors['terminal_bg'],
                                     fg=self.colors['terminal_fg'],
                                     wrap=tk.WORD,
                                     relief=tk.FLAT,
                                     insertbackground=self.colors['terminal_fg'],
                                     padx=8, pady=6)
        self.terminal_text.pack(fill=tk.BOTH, expand=True)
        self.terminal_text.configure(state=tk.DISABLED)
        
        term_input_frame = tk.Frame(terminal_panel, bg=self.colors['bg2'], relief=tk.FLAT, bd=1)
        term_input_frame.pack(fill=tk.X, pady=(4, 0))
        
        self.terminal_entry = tk.Entry(term_input_frame,
                                       font=("Courier New", 9),
                                       bg=self.colors['bg2'],
                                       fg=self.colors['terminal_fg'],
                                       relief=tk.FLAT,
                                       insertbackground=self.colors['terminal_fg'])
        self.terminal_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=4)
        self.terminal_entry.bind('<Return>', self.execute_terminal_command)
        
        self.term_run_btn = tk.Button(term_input_frame, text="▶ RUN",
                                      command=self.execute_terminal_command,
                                      font=("Courier New", 8, "bold"),
                                      bg=self.colors['bg3'], fg=self.colors['fg'],
                                      relief=tk.FLAT,
                                      padx=10, pady=4,
                                      cursor='hand2')
        self.term_run_btn.pack(side=tk.RIGHT, padx=5, pady=4)
        
        # Footer with credits (clickable)
        footer = tk.Frame(main_frame, bg=self.colors['bg2'], height=30)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)
        
        credit_label = tk.Label(footer, text="🔒 Black by @S_MOKE_R | ", font=("Courier New", 8),
                                fg=self.colors['fg2'], bg=self.colors['bg2'])
        credit_label.pack(side=tk.LEFT, padx=10)
        
        # GitHub link (clickable)
        github_btn = tk.Label(footer, text="GitHub", font=("Courier New", 8, "underline"),
                              fg=self.colors['accent'], bg=self.colors['bg2'], cursor='hand2')
        github_btn.pack(side=tk.LEFT)
        github_btn.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/S-MOKE-R"))
        
        tk.Label(footer, text=" | ", font=("Courier New", 8),
                fg=self.colors['fg2'], bg=self.colors['bg2']).pack(side=tk.LEFT)
        
        # Telegram link (clickable)
        tg_btn = tk.Label(footer, text="Telegram", font=("Courier New", 8, "underline"),
                          fg=self.colors['accent'], bg=self.colors['bg2'], cursor='hand2')
        tg_btn.pack(side=tk.LEFT)
        tg_btn.bind("<Button-1>", lambda e: webbrowser.open("https://t.me/S_MOKE_R"))
        
        tk.Label(footer, text=" | ", font=("Courier New", 8),
                fg=self.colors['fg2'], bg=self.colors['bg2']).pack(side=tk.LEFT)
        
        # Channel link (clickable)
        channel_btn = tk.Label(footer, text="Channel", font=("Courier New", 8, "underline"),
                               fg=self.colors['accent'], bg=self.colors['bg2'], cursor='hand2')
        channel_btn.pack(side=tk.LEFT)
        channel_btn.bind("<Button-1>", lambda e: webbrowser.open("https://t.me/VOID_SMOKER"))
        
        tk.Label(footer, text=" | Open Source", font=("Courier New", 8),
                fg=self.colors['fg2'], bg=self.colors['bg2']).pack(side=tk.LEFT, padx=5)
        
        self.update_history_count()

    def update_history_count(self):
        count = len(self.history)
        self.history_label.config(text=f"📜 {count}")

    def setup_shortcuts(self):
        self.root.bind('<Control-c>', lambda e: self.clear_chat())
        self.root.bind('<Control-t>', lambda e: self.terminal_entry.focus_set())
        self.root.bind('<Escape>', lambda e: self.input_entry.focus_set())
        self.root.bind('<Control-h>', lambda e: self.show_history())
        self.root.bind('<Control-s>', lambda e: self.show_settings())
    
    def handle_enter(self, event):
        if event.state & 0x1:
            return
        self.send_message()
        return "break"
    
    def add_message(self, sender, message):
        if sender == "system":
            frame = tk.Frame(self.messages_frame, bg=self.colors['bg'])
            frame.pack(fill=tk.X, pady=2)
            label = tk.Label(frame, text=f"── {message} ──",
                           font=("Courier New", 8, "italic"),
                           fg=self.colors['fg2'], bg=self.colors['bg'])
            label.pack()
            self.scroll_to_bottom()
            return
        
        bg_color = self.colors['user_bubble'] if sender == "user" else self.colors['ai_bubble']
        align = "e" if sender == "user" else "w"
        name = f"{self.user_name}@black:/$" if sender == "user" else "BLACK"
        text_color = self.colors['fg'] if sender == "user" else self.colors['accent']
        
        frame = tk.Frame(self.messages_frame, bg=self.colors['bg'])
        frame.pack(fill=tk.X, pady=2)
        
        container = tk.Frame(frame, bg=bg_color, relief=tk.FLAT, bd=0)
        container.pack(side=tk.LEFT if align == "w" else tk.RIGHT, padx=6, pady=2, ipadx=10, ipady=4)
        
        name_label = tk.Label(container, text=name, font=("Courier New", 7, "bold"),
                             fg=self.colors['fg2'], bg=bg_color)
        name_label.pack(anchor=tk.W)
        
        msg_label = tk.Label(container, text=message, font=("Courier New", 9),
                            fg=text_color, bg=bg_color, wraplength=600, justify=tk.LEFT)
        msg_label.pack(anchor=tk.W)
        
        self.scroll_to_bottom()
        self.update_history_count()
    
    def add_terminal(self, text):
        self.terminal_text.configure(state=tk.NORMAL)
        self.terminal_text.insert(tk.END, text + "\n")
        self.terminal_text.see(tk.END)
        self.terminal_text.configure(state=tk.DISABLED)
    
    def scroll_to_bottom(self):
        self.chat_canvas.yview_moveto(1.0)
        self.root.update_idletasks()
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        self.chat_canvas.yview_moveto(1.0)
    
    def set_status(self, text, color='accent'):
        self.status_label.config(text=text)
        self.status_dot.itemconfig("dot", fill=self.colors[color])
    
    def quick_action(self, action):
        if action == "clear":
            self.clear_chat()
            return
        
        if action == "history":
            self.show_history()
            return
        
        if action == "search":
            self.add_message("system", "🔍 Type: search <keyword>")
            return
        
        if action == "menu":
            self.add_message("assistant", "🔥 Type 'scan target.com' for reconnaissance.")
            self.add_terminal("> Menu shown in chat")
            return
        
        if action == "scan":
            self.add_message("system", "⚡ Enter target to scan (e.g., example.com)")
            return
        
        self.add_message("user", action)
        self.process_command(action)
    
    def show_history(self):
        if not self.history:
            self.add_message("system", "📜 No history yet.")
            return
        
        self.add_message("system", f"📜 Last {len(self.history[-10:])} interactions:")
        for item in self.history[-10:]:
            self.add_message("system", f"Q: {item['question'][:60]}...")
            self.add_message("system", f"A: {item['answer'][:60]}...")
            self.add_message("system", "-" * 30)
    
    def clear_chat(self):
        for widget in self.messages_frame.winfo_children():
            widget.destroy()
        self.add_message("system", "CHAT CLEARED")
        self.add_message("assistant", "How can I help you?")
    
    def send_message(self):
        user_input = self.input_entry.get(1.0, tk.END).strip()
        if not user_input:
            return
        
        self.input_entry.delete(1.0, tk.END)
        self.add_message("user", user_input)
        self.process_command(user_input)
    
    def process_command(self, user_input):
        if user_input.lower() == 'menu':
            self.add_message("assistant", "🔥 Type 'scan target.com' for reconnaissance.")
            self.add_terminal("> Menu shown in chat")
            return
        
        if user_input.lower() == 'history':
            self.show_history()
            return
        
        if user_input.lower().startswith('search '):
            keyword = user_input[7:].strip()
            results = []
            for item in self.history:
                if keyword.lower() in item['question'].lower() or keyword.lower() in item['answer'].lower():
                    results.append(item)
            if results:
                self.add_message("system", f"🔍 Found {len(results)} results for '{keyword}':")
                for item in results[:5]:
                    self.add_message("system", f"Q: {item['question'][:50]}...")
            else:
                self.add_message("system", f"No results for '{keyword}'")
            return
        
        if user_input.lower() == 'clear':
            self.history = []
            self.save_history()
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            c.execute("DELETE FROM interactions")
            conn.commit()
            conn.close()
            self.add_message("system", "🧹 History cleared!")
            self.update_history_count()
            return
        
        if user_input.lower() == 'repeat':
            if self.last_question and self.last_answer:
                self.add_message("system", f"📝 Last Q: {self.last_question}")
                self.add_message("system", f"📝 Last A: {self.last_answer}")
            else:
                self.add_message("system", "No previous interaction.")
            return
        
        if self.mode == "full" and user_input.startswith('run '):
            cmd = user_input[4:].strip()
            self.execute_command(cmd)
            return
        
        self.set_status("THINKING...", 'warning')
        threading.Thread(target=self.get_black_response, args=(user_input,), daemon=True).start()
    
    def get_black_response(self, user_input):
        try:
            env = os.environ.copy()
            env["BLACK_API_KEY"] = self.api_key
            env["BLACK_USER_NAME"] = self.user_name
            
            result = subprocess.run([self.black_script, user_input],
                                  capture_output=True, text=True, timeout=90,
                                  env=env)
            
            response = result.stdout.strip()
            if not response or "Error" in response:
                response = "I couldn't process that. Try again."
            
            self.root.after(0, lambda: self.add_message("assistant", response))
            self.root.after(0, lambda: self.set_status("READY", 'accent'))
            self.root.after(0, lambda: self.add_interaction(user_input, response))
            
            if "COMMAND:" in response and self.mode == "full":
                cmd_line = response.split('\n')[0]
                if cmd_line.startswith("COMMAND:"):
                    cmd = cmd_line.replace("COMMAND:", "").strip()
                    if cmd and cmd != "N/A" and cmd != "None":
                        self.root.after(0, lambda: self.execute_command(cmd))
            
        except Exception as e:
            self.root.after(0, lambda: self.add_message("assistant", f"Error: {str(e)}"))
            self.root.after(0, lambda: self.set_status("READY", 'accent'))
    
    def execute_command(self, cmd):
        if self.mode != "full":
            self.add_message("system", "⚠️ Command execution is disabled in Normal mode.")
            return
        
        self.add_terminal(f"> {cmd}")
        self.add_message("system", f"⚡ EXECUTING: {cmd}")
        self.set_status("EXECUTING...", 'warning')
        
        def run_thread():
            try:
                process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                def read_output():
                    while True:
                        output = process.stdout.readline()
                        if output == '' and process.poll() is not None:
                            break
                        if output:
                            self.root.after(0, lambda: self.add_terminal(output.strip()))
                
                output_thread = threading.Thread(target=read_output, daemon=True)
                output_thread.start()
                
                try:
                    process.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    process.kill()
                    self.root.after(0, lambda: self.add_terminal("❌ COMMAND TIMED OUT"))
                    self.root.after(0, lambda: self.set_status("READY", 'accent'))
                    return
                
                stderr = process.stderr.read()
                if stderr:
                    self.root.after(0, lambda: self.add_terminal(f"Error: {stderr.strip()}"))
                
                if process.returncode == 0:
                    self.root.after(0, lambda: self.add_terminal("✅ COMPLETED"))
                    self.root.after(0, lambda: self.add_message("system", "✅ Command executed"))
                else:
                    self.root.after(0, lambda: self.add_terminal(f"❌ FAILED (code: {process.returncode})"))
                    self.root.after(0, lambda: self.add_message("system", f"❌ Command failed"))
                
                self.root.after(0, lambda: self.set_status("READY", 'accent'))
                
            except Exception as e:
                self.root.after(0, lambda: self.add_terminal(f"❌ Error: {str(e)}"))
                self.root.after(0, lambda: self.add_message("system", f"❌ Error: {str(e)}"))
                self.root.after(0, lambda: self.set_status("READY", 'accent'))
        
        threading.Thread(target=run_thread, daemon=True).start()
    
    def execute_terminal_command(self, event=None):
        if self.mode != "full":
            self.add_message("system", "⚠️ Terminal commands are disabled in Normal mode.")
            return
        
        cmd = self.terminal_entry.get().strip()
        if not cmd:
            return
        
        self.terminal_entry.delete(0, tk.END)
        self.execute_command(cmd)
    
    def show_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙️ Black Settings")
        settings_window.geometry("500x550")
        settings_window.configure(bg=self.colors['bg'])
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Title
        tk.Label(settings_window, text="⚙️ Settings", font=("Courier New", 16, "bold"),
                fg=self.colors['fg'], bg=self.colors['bg']).pack(pady=15)
        
        # Credits section with clickable links
        credits_frame = tk.Frame(settings_window, bg=self.colors['bg2'], padx=10, pady=10)
        credits_frame.pack(padx=20, pady=5, fill=tk.X)
        
        tk.Label(credits_frame, text="👨‍💻 Credits", font=("Courier New", 10, "bold"),
                fg=self.colors['fg'], bg=self.colors['bg2']).pack(anchor=tk.W)
        
        tk.Label(credits_frame, text="Developer: @S_MOKE_R", font=("Courier New", 9),
                fg=self.colors['fg2'], bg=self.colors['bg2']).pack(anchor=tk.W)
        
        # GitHub link (clickable)
        github_frame = tk.Frame(credits_frame, bg=self.colors['bg2'])
        github_frame.pack(anchor=tk.W)
        tk.Label(github_frame, text="GitHub: ", font=("Courier New", 9),
                fg=self.colors['fg2'], bg=self.colors['bg2']).pack(side=tk.LEFT)
        github_link = tk.Label(github_frame, text="https://github.com/S-MOKE-R", font=("Courier New", 9, "underline"),
                               fg=self.colors['accent'], bg=self.colors['bg2'], cursor='hand2')
        github_link.pack(side=tk.LEFT)
        github_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/S-MOKE-R"))
        
        # Telegram link (clickable)
        tg_frame = tk.Frame(credits_frame, bg=self.colors['bg2'])
        tg_frame.pack(anchor=tk.W)
        tk.Label(tg_frame, text="Telegram: ", font=("Courier New", 9),
                fg=self.colors['fg2'], bg=self.colors['bg2']).pack(side=tk.LEFT)
        tg_link = tk.Label(tg_frame, text="https://t.me/S_MOKE_R", font=("Courier New", 9, "underline"),
                           fg=self.colors['accent'], bg=self.colors['bg2'], cursor='hand2')
        tg_link.pack(side=tk.LEFT)
        tg_link.bind("<Button-1>", lambda e: webbrowser.open("https://t.me/S_MOKE_R"))
        
        # Channel link (clickable)
        channel_frame = tk.Frame(credits_frame, bg=self.colors['bg2'])
        channel_frame.pack(anchor=tk.W)
        tk.Label(channel_frame, text="Channel: ", font=("Courier New", 9),
                fg=self.colors['fg2'], bg=self.colors['bg2']).pack(side=tk.LEFT)
        channel_link = tk.Label(channel_frame, text="https://t.me/VOID_SMOKER", font=("Courier New", 9, "underline"),
                                fg=self.colors['accent'], bg=self.colors['bg2'], cursor='hand2')
        channel_link.pack(side=tk.LEFT)
        channel_link.bind("<Button-1>", lambda e: webbrowser.open("https://t.me/VOID_SMOKER"))
        
        # API Key
        tk.Label(settings_window, text="Logfare API Key:", font=("Courier New", 10),
                fg=self.colors['fg'], bg=self.colors['bg']).pack(anchor=tk.W, padx=20, pady=(10,0))
        
        api_entry = tk.Entry(settings_window, font=("Courier New", 10),
                             bg=self.colors['bg2'], fg=self.colors['fg'],
                             width=50)
        api_entry.pack(padx=20, pady=5)
        api_entry.insert(0, self.api_key)
        
        # Instructions
        inst_frame = tk.Frame(settings_window, bg=self.colors['bg'])
        inst_frame.pack(padx=20, pady=5, fill=tk.X)
        tk.Label(inst_frame, text="📌 Get your API key at: https://logfare.ai/register",
                font=("Courier New", 8), fg=self.colors['fg2'], bg=self.colors['bg']).pack(anchor=tk.W)
        
        # User Name
        tk.Label(settings_window, text="Your Name:", font=("Courier New", 10),
                fg=self.colors['fg'], bg=self.colors['bg']).pack(anchor=tk.W, padx=20)
        
        name_entry = tk.Entry(settings_window, font=("Courier New", 10),
                             bg=self.colors['bg2'], fg=self.colors['fg'],
                             width=50)
        name_entry.pack(padx=20, pady=5)
        name_entry.insert(0, self.user_name)
        
        # Mode Selection
        tk.Label(settings_window, text="Mode:", font=("Courier New", 10),
                fg=self.colors['fg'], bg=self.colors['bg']).pack(anchor=tk.W, padx=20)
        
        mode_frame = tk.Frame(settings_window, bg=self.colors['bg'])
        mode_frame.pack(padx=20, pady=5, fill=tk.X)
        
        mode_var = tk.StringVar(value=self.mode)
        normal_radio = tk.Radiobutton(mode_frame, text="Normal (Suggest commands only)",
                                      variable=mode_var, value="normal",
                                      bg=self.colors['bg'], fg=self.colors['fg'],
                                      selectcolor=self.colors['bg'])
        normal_radio.pack(anchor=tk.W)
        full_radio = tk.Radiobutton(mode_frame, text="Full (Execute commands via terminal)",
                                    variable=mode_var, value="full",
                                    bg=self.colors['bg'], fg=self.colors['fg'],
                                    selectcolor=self.colors['bg'])
        full_radio.pack(anchor=tk.W)
        
        # Mode description
        desc_label = tk.Label(settings_window, 
                              text="Normal: Black suggests commands only.\nFull: Black can execute commands (requires confirmation).",
                              font=("Courier New", 8), fg=self.colors['fg2'], bg=self.colors['bg'],
                              justify=tk.LEFT)
        desc_label.pack(padx=20, pady=5, anchor=tk.W)
        
        # Save button
        def save_settings():
            api_key = api_entry.get().strip()
            user_name = name_entry.get().strip()
            mode = mode_var.get()
            
            if not api_key:
                messagebox.showerror("Error", "API key is required.")
                return
            if not user_name:
                user_name = "hacker"
            
            self.config["api_key"] = api_key
            self.config["user_name"] = user_name
            self.config["mode"] = mode
            self.save_config()
            
            self.api_key = api_key
            self.user_name = user_name
            self.mode = mode
            self.mode_label.config(text="🔓 NORMAL" if mode == "normal" else "⚡ FULL")
            
            settings_window.destroy()
            messagebox.showinfo("Settings", "Settings saved successfully!")
        
        save_btn = tk.Button(settings_window, text="💾 Save Settings",
                            command=save_settings,
                            font=("Courier New", 10, "bold"),
                            bg=self.colors['accent'], fg='black',
                            relief=tk.FLAT, padx=20, pady=8,
                            cursor='hand2')
        save_btn.pack(pady=15)

def main():
    root = tk.Tk()
    app = BlackGUI(root)
    
    def on_closing():
        if messagebox.askokcancel("Quit", "Exit Black?"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
