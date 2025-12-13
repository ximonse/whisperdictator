import tkinter as tk
from tkinter import ttk
import threading
import time
import pyperclip
import sounddevice as sd
import numpy as np
import wave
import tempfile
import os
import whisper

# Sätt FFmpeg-sökväg (cross-platform)
import platform
script_dir = os.path.dirname(os.path.abspath(__file__))
if platform.system() == "Windows":
    ffmpeg_path = os.path.join(script_dir, "ffmpeg.exe")
    if os.path.exists(ffmpeg_path):
        os.environ["PATH"] = script_dir + os.pathsep + os.environ.get("PATH", "")
# På Linux/Mac förväntas ffmpeg vara installerat via pakethanteraren

class Diktafon:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Diktafon")
        
        # 90-tals stil: grå bakgrund, raised knappar
        self.root.configure(bg='#c0c0c0')
        self.root.geometry("200x50")  # Extremt kompakt storlek
        self.root.resizable(False, False)
        self.root.attributes('-topmost', True)  # Alltid överst
        self.root.attributes('-alpha', 0.6)  # Ljusare transparens - tydligare
        
        # Bind hover events för transparens på hela fönstret
        self.root.bind('<Enter>', self.on_hover_enter)
        self.root.bind('<Leave>', self.on_hover_leave)
        
        # Global hotkey - högerpil+shift istället för högerpil+enter
        self.setup_global_hotkey()
        
        # Status variabler
        self.is_recording = False
        self.is_paused = False
        self.recorded_audio = []
        self.transcribed_text = ""
        
        # Tidsräkning
        self.recording_start_time = None
        self.total_recording_time = 0
        self.timer_thread = None
        
        # Global hotkey variabler
        self.hotkey_listener = None
        self.hotkey_pressed = {'shift_r': False, 'right': False}
        self.hotkey_callback = None
        self.hotkey_recording = False
        
        # Ljudinspelning variabler (sounddevice)
        self.audio_frames = []
        self.audio_file_path = None
        self.stream = None
        
        # Ljudinställningar - Whisper-vänligt format
        self.channels = 1  # Mono
        self.rate = 16000  # 16kHz för Whisper
        self.dtype = np.int16
        
        # Ladda Whisper-modell (görs en gång)
        self.whisper_model = None
        
        self.setup_gui()
        
        # Bind hover events efter GUI är skapad
        self.root.after(100, self.bind_hover_events)
        
        # Ladda Whisper efter GUI är skapad
        self.load_whisper_model()
        
    def setup_gui(self):
        # Huvudframe med grå 90-tals känsla
        main_frame = tk.Frame(self.root, bg='#c0c0c0', relief='flat', bd=0)
        main_frame.pack(fill='both', expand=True, padx=1, pady=1)
        
        # Status frame för status + timer
        status_frame = tk.Frame(main_frame, bg='#c0c0c0')
        status_frame.pack(fill='x', padx=1, pady=0)
        
        # Status label med indragen stil + inbyggd progressbar
        self.status_label = tk.Label(
            status_frame, 
            text="Redo", 
            bg='#ffffff', 
            relief='flat', 
            bd=0,
            font=('MS Sans Serif', 6),
            anchor='w',
            height=1
        )
        self.status_label.pack(side='left', fill='x', expand=True)
        
        # Progress state för status-området
        self.progress_active = False
        self.progress_thread = None
        
        # Timer label
        self.timer_label = tk.Label(
            status_frame,
            text="00:00",
            bg='#ffffff',
            relief='flat',
            bd=0,
            font=('MS Sans Serif', 6),
            width=5
        )
        self.timer_label.pack(side='right', padx=(1,0))
        
        
        # Knapp-frame
        button_frame = tk.Frame(main_frame, bg='#c0c0c0')
        button_frame.pack(fill='both', expand=True, padx=0, pady=0)
        
        # Extremt kompakta knappar - stor röd play-ikon
        self.rec_button = tk.Button(
            button_frame, 
            text="▶", 
            command=self.toggle_recording,
            bg='#c0c0c0', 
            relief='flat', 
            bd=0,
            font=('MS Sans Serif', 20, 'bold'),
            fg='red',
            width=2,
            height=1,
            pady=0
        )
        self.rec_button.pack(side='left', padx=0, pady=0, fill='y')
        
        self.stop_button = tk.Button(
            button_frame, 
            text="■", 
            command=self.stop_and_transcribe,
            bg='#c0c0c0', 
            relief='flat', 
            bd=0,
            font=('MS Sans Serif', 16, 'bold'),
            fg='black',
            width=2,
            height=1,
            state='disabled',
            pady=0
        )
        self.stop_button.pack(side='left', padx=0, pady=0, fill='y')
        
        self.clear_button = tk.Button(
            button_frame, 
            text="🗑", 
            command=self.clear_recording,
            bg='#c0c0c0', 
            relief='flat', 
            bd=0,
            font=('MS Sans Serif', 14),
            width=2,
            height=1,
            pady=0
        )
        self.clear_button.pack(side='left', padx=0, pady=0, fill='y')
        
        # AI stjärn-knapp - grå från början
        self.ai_button = tk.Button(
            button_frame, 
            text="★", 
            command=self.copy_with_ai_prompt,
            bg='#c0c0c0', 
            relief='flat', 
            bd=0,
            font=('MS Sans Serif', 16, 'bold'),
            fg='#808080',
            width=2,
            height=1,
            state='disabled',
            pady=0
        )
        self.ai_button.pack(side='left', padx=0, pady=0, fill='y')
        
        
    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        elif not self.is_paused:
            self.pause_recording()
        else:
            self.resume_recording()
            
    def start_recording(self):
        self.is_recording = True
        self.is_paused = False
        self.audio_frames = []  # Rensa tidigare inspelning
        
        # Starta timer - nollställ bara vid NY inspelning
        self.recording_start_time = time.time()
        self.total_recording_time = 0
        self.timer_label.config(text="00:00")  # Nollställ timer vid NY inspelning
        self.start_timer()
        
        self.status_label.config(text="● SPELAR IN", fg='red')
        self.rec_button.config(text="⏸", relief='sunken')
        self.stop_button.config(state='normal')
        
        # Starta ljudinspelning (sounddevice)
        try:
            def audio_callback(indata, frames, time_info, status):
                if self.is_recording and not self.is_paused:
                    self.audio_frames.append(indata.copy())
            
            # Hitta första input-device
            input_device = sd.default.device[0]
            if input_device is None or input_device < 0:
                # Sök efter första device med input
                for i, dev in enumerate(sd.query_devices()):
                    if dev['max_input_channels'] > 0:
                        input_device = i
                        break
            
            self.stream = sd.InputStream(
                device=input_device,
                samplerate=self.rate,
                channels=self.channels,
                dtype=self.dtype,
                callback=audio_callback
            )
            self.stream.start()
            
            print("Startar inspelning...")
            
        except Exception as e:
            print(f"Kunde inte starta inspelning: {e}")
            self.status_label.config(text="Mikrofonfel", fg='red')
        
            
    def pause_recording(self):
        self.is_paused = True
        
        # Uppdatera total tid
        if self.recording_start_time:
            self.total_recording_time += time.time() - self.recording_start_time
        
        self.status_label.config(text="⏸ PAUSAD", fg='orange')
        self.rec_button.config(text="▶", relief='raised')
        
        # Pausa ljudinspelning (sounddevice hanteras via is_paused flaggan)
        # Ingen explicit stopp behövs - callback ignorerar data när is_paused=True
        
        print("Pausar inspelning...")
        
    def resume_recording(self):
        self.is_paused = False
        
        # Starta om timer från nuvarande tidpunkt
        self.recording_start_time = time.time()
        
        self.status_label.config(text="● SPELAR IN", fg='red')
        self.rec_button.config(text="⏸", relief='sunken')
        
        # Återuppta ljudinspelning (sounddevice hanteras via is_paused flaggan)
        # Ingen explicit start behövs - callback samlar data när is_paused=False
        
        print("Återupptar inspelning...")
        
    def stop_and_transcribe(self):
        self.is_recording = False
        self.is_paused = False
        
        # Stoppa timer och beräkna total tid, nollställ timer
        if self.recording_start_time:
            self.total_recording_time += time.time() - self.recording_start_time
            self.recording_start_time = None
        
        # BEHÅLL timer vid stopp - nollställs bara vid ny inspelning eller app-stängning
        
        self.status_label.config(text="⏳ SPARAR...", fg='blue')
        
        # Stoppa ljudinspelning (sounddevice)
        try:
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None
        except Exception as e:
            print(f"Stoppfel: {e}")
            self.stream = None
        
        # Återställ knappar
        self.rec_button.config(text="▶", relief='raised')
        self.stop_button.config(state='disabled')
        
        # Spara inspelning och transkribera
        print("Stoppar och transkriberar...")
        threading.Thread(target=self.save_and_transcribe, daemon=True).start()
        
    def load_whisper_model(self):
        """Ladda Whisper-modell i bakgrund"""
        def load_model():
            try:
                self.start_status_progress("Laddar", 5)  # 5 sekunder uppskattad tid
                self.whisper_model = whisper.load_model("small")
                print("Whisper-modell laddad")
                self.stop_status_progress("Redo")
            except Exception as e:
                print(f"Kunde inte ladda Whisper: {e}")
                self.stop_status_progress("Laddningsfel", 'red')
        
        # Ladda modell i bakgrund så GUI inte fryser
        threading.Thread(target=load_model, daemon=True).start()
    
    def transcribe_with_whisper(self):
        """Transkribera ljudfil med Whisper"""
        self.status_label.config(text="⏳ TRANSKRIBERAR...", fg='blue')
        
        # Starta status-progressbar med kalibrerad tid (16s tal = 28s transkription)
        estimated_time = max(5, int(self.total_recording_time * 1.75))  # 1.75x baserat på din data
        self.start_status_progress("Transkriberar", estimated_time)
        
        try:
            if self.whisper_model is None:
                self.stop_status_progress("Modell ej laddad", 'red')
                return
            
            # Transkribera med Whisper - förbättrade inställningar
            result = self.whisper_model.transcribe(
                self.audio_file_path,
                language="sv",  # Svenska
                verbose=False,
                temperature=0,  # Mer deterministisk
                best_of=1,      # Fler försök för bättre kvalitet
                beam_size=1,    # Bättre sökning
                word_timestamps=False,
                condition_on_previous_text=False  # Undvik driftning
            )
            
            # Hämta text från resultat
            self.transcribed_text = result["text"].strip()
            
            if self.transcribed_text:
                # Spara transkription till textfil
                self.save_transcription()
                
                # Kopiera transkription direkt (utan AI-prompt)
                try:
                    pyperclip.copy(self.transcribed_text)
                    print("Transkription kopierad till urklipp")
                except Exception as e:
                    print(f"Kunde inte kopiera: {e}")
                
                self.stop_status_progress("✓ KLART", 'green')
                # Aktivera och gör stjärnan grön
                self.ai_button.config(state='normal', bg='#90EE90', fg='#006400')
                print(f"Transkription: {self.transcribed_text}")
            else:
                self.stop_status_progress("Inget tal", 'orange')
            
        except Exception as e:
            print(f"Transkriptionsfel: {e}")
            print(f"Feltyp: {type(e)}")
            import traceback
            print("Fullständig traceback:")
            traceback.print_exc()
            
            # Specifik hantering för Whisper tensor-fel
            if "cannot reshape tensor" in str(e):
                self.stop_status_progress("För kort inspelning för Whisper", 'orange')
            elif "No such file or directory" in str(e):
                self.stop_status_progress("Ljudfil saknas", 'red')
            elif "ffmpeg" in str(e).lower():
                self.stop_status_progress("FFmpeg saknas", 'red')
            else:
                self.stop_status_progress("Transkriptionsfel", 'red')
        
        # Blink-effekt när färdig
        self.blink_completion()
        
        # Återställ status efter 3 sekunder
        def reset_status():
            time.sleep(3)
            self.status_label.config(text="Redo", fg='black')
        
        threading.Thread(target=reset_status, daemon=True).start()
    
    def save_transcription(self):
        """Spara transkription till textfil"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            transcription_dir = os.path.join(script_dir, "transcriptions")
            os.makedirs(transcription_dir, exist_ok=True)
            
            # Timestamp för filnamn
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            text_file_path = os.path.join(transcription_dir, f"transcription_{timestamp}.txt")
            
            with open(text_file_path, 'w', encoding='utf-8') as f:
                f.write(self.transcribed_text)
            
            print(f"Transkription sparad: {text_file_path}")
            
        except Exception as e:
            print(f"Kunde inte spara transkription: {e}")
        
    def record_audio(self):
        """Inte längre använd - sounddevice callback hanterar inspelning"""
        pass
    
    def start_new_stream(self):
        """Skapa ny stream om den gamla är trasig (sounddevice)"""
        try:
            if self.stream:
                try:
                    self.stream.close()
                except:
                    pass
                self.stream = None
            
            time.sleep(0.1)
            
            def audio_callback(indata, frames, time_info, status):
                if self.is_recording and not self.is_paused:
                    self.audio_frames.append(indata.copy())
            
            # Hitta första input-device
            input_device = sd.default.device[0]
            if input_device is None or input_device < 0:
                # Sök efter första device med input
                for i, dev in enumerate(sd.query_devices()):
                    if dev['max_input_channels'] > 0:
                        input_device = i
                        break
            
            self.stream = sd.InputStream(
                device=input_device,
                samplerate=self.rate,
                channels=self.channels,
                dtype=self.dtype,
                callback=audio_callback
            )
            self.stream.start()
            print("Ny stream skapad")
        except Exception as e:
            print(f"Kunde inte skapa ny stream: {e}")
            self.status_label.config(text="Mikrofonfel", fg='red')
    
    def save_and_transcribe(self):
        """Spara ljudfil och starta transkription"""
        if not self.audio_frames:
            self.stop_status_progress("Ingen audio", 'red')
            return
        
        # Kombinera numpy arrays till en
        total_audio_data = np.concatenate(self.audio_frames, axis=0)
        if len(total_audio_data) < 1600:  # Minst 0.1 sekund
            self.stop_status_progress("För kort inspelning", 'orange')
            return
            
        # Skapa fil för ljudet i ljudfiler-mappen
        script_dir = os.path.dirname(os.path.abspath(__file__))
        audio_dir = os.path.join(script_dir, "recordings")
        os.makedirs(audio_dir, exist_ok=True)
        
        # Timestamp för unikt filnamn
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.audio_file_path = os.path.join(audio_dir, f"recording_{timestamp}.wav")
        
        try:
            # Spara WAV-fil (sounddevice/numpy)
            import scipy.io.wavfile as wavfile
            wavfile.write(self.audio_file_path, self.rate, total_audio_data)
            
            print(f"Ljudfil sparad: {self.audio_file_path}")
            print(f"Audio-data storlek: {len(total_audio_data)} bytes")
            
            # Transkribera med Whisper
            self.transcribe_with_whisper()
            
        except Exception as e:
            print(f"Kunde inte spara ljudfil: {e}")
            print(f"Feltyp: {type(e)}")
            import traceback
            traceback.print_exc()
            self.stop_status_progress("Sparfel", 'red')
    
    def clear_recording(self):
        self.is_recording = False
        self.is_paused = False
        self.audio_frames = []
        self.transcribed_text = ""
        
        # Stäng stream om öppen (sounddevice)
        try:
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None
        except Exception as e:
            print(f"Stängningsfel: {e}")
            self.stream = None
        
        # Ta bort temp-fil
        if self.audio_file_path and os.path.exists(self.audio_file_path):
            try:
                os.remove(self.audio_file_path)
            except:
                pass
        
        # Återställ timer bara vid RENSA
        self.recording_start_time = None
        self.total_recording_time = 0
        self.timer_label.config(text="00:00")
        
        # Stoppa eventuell progress
        self.stop_status_progress("Redo")
        
        # Återställ GUI
        self.status_label.config(text="Redo", fg='black')
        self.rec_button.config(text="▶", relief='raised')
        self.stop_button.config(state='disabled')
        # Återställ stjärn-knapp till grå
        self.ai_button.config(state='disabled', bg='#c0c0c0', fg='#808080')
        
        print("Rensar inspelning...")
        
    def copy_with_ai_prompt(self):
        if self.transcribed_text:
            # Läs AI-prompt från fil
            try:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                prompt_file = os.path.join(script_dir, "ai-prompt.txt")
                
                if os.path.exists(prompt_file):
                    with open(prompt_file, 'r', encoding='utf-8') as f:
                        prompt = f.read().strip() + "\n\n"
                else:
                    # Fallback om filen saknas
                    prompt = "Renskriv och organisera texten så det blir tydligt.\n\n"
            except Exception as e:
                print(f"Kunde inte läsa ai-prompt.txt: {e}")
                prompt = "Renskriv och organisera texten så det blir tydligt.\n\n"
            
            full_text = prompt + self.transcribed_text
            
            try:
                pyperclip.copy(full_text)
                self.status_label.config(text="★ KOPIERAT", fg='green')
                
                # Återställ efter 2 sekunder
                def reset_status():
                    time.sleep(2)
                    self.status_label.config(text="Redo", fg='black')
                
                threading.Thread(target=reset_status, daemon=True).start()
                
            except Exception as e:
                print(f"Kunde inte kopiera: {e}")
                self.status_label.config(text="Kopieringsfel", fg='red')
    
    def start_timer(self):
        """Starta tidsräknare för inspelning"""
        if self.timer_thread is None or not self.timer_thread.is_alive():
            self.timer_thread = threading.Thread(target=self.update_timer, daemon=True)
            self.timer_thread.start()
    
    def update_timer(self):
        """Uppdatera timer kontinuerligt"""
        while self.is_recording:
            if not self.is_paused and self.recording_start_time:
                current_session = time.time() - self.recording_start_time
                total_time = self.total_recording_time + current_session
                
                minutes = int(total_time // 60)
                seconds = int(total_time % 60)
                time_str = f"{minutes:02d}:{seconds:02d}"
                
                # Uppdatera GUI säkert
                self.root.after(0, lambda: self.timer_label.config(text=time_str))
                
            time.sleep(1)
    
    def start_status_progress(self, message, estimated_seconds):
        """Starta progressbar i status-fältet"""
        self.progress_active = True
        self.status_label.config(text=f"{message}...", fg='blue')
        
        def animate_progress():
            dots = 0
            start_time = time.time()
            
            while self.progress_active:
                elapsed = time.time() - start_time
                progress_percent = min(95, (elapsed / estimated_seconds) * 100)
                
                # Animera med prickar
                dot_count = (dots % 4)
                dot_str = "." * dot_count
                
                # Visa progress i procent efter meddelandet
                if elapsed > 1:  # Visa procent efter 1 sekund
                    display_text = f"{message} {int(progress_percent)}%{dot_str}"
                else:
                    display_text = f"{message}{dot_str}"
                
                self.root.after(0, lambda: self.status_label.config(text=display_text))
                
                time.sleep(0.5)
                dots += 1
                
                # Auto-stop efter max tid
                if elapsed >= estimated_seconds * 1.5:
                    break
        
        self.progress_thread = threading.Thread(target=animate_progress, daemon=True)
        self.progress_thread.start()
    
    def stop_status_progress(self, final_message, color='black'):
        """Stoppa progressbar och sätt slutmeddelande"""
        self.progress_active = False
        self.status_label.config(text=final_message, fg=color)
    
    def on_hover_enter(self, event):
        """Gör helt synlig vid hover"""
        self.root.attributes('-alpha', 1.0)
    
    def on_hover_leave(self, event):
        """Återgå till transparens"""
        self.root.attributes('-alpha', 0.6)
    
    def blink_completion(self):
        """Blink-effekt när transkription är färdig"""
        def blink():
            for _ in range(3):
                self.root.attributes('-alpha', 1.0)
                time.sleep(0.15)
                self.root.attributes('-alpha', 0.6)
                time.sleep(0.15)
        
        threading.Thread(target=blink, daemon=True).start()
    
    def setup_global_hotkey(self):
        """Konfigurera global hotkey - högerpil+shift"""
        try:
            import pynput
            from pynput import keyboard
            
            def on_hotkey_start():
                try:
                    # Starta/återuppta inspelning när båda tangenterna trycks ned
                    if not self.hotkey_recording:
                        print("Push-to-talk: Startar/återupptar inspelning")
                        self.hotkey_recording = True
                        if not self.is_recording:
                            self.root.after(0, self.start_recording)
                        elif self.is_paused:
                            self.root.after(0, self.resume_recording)
                except Exception as e:
                    print(f"Hotkey start-fel: {e}")
            
            def on_hotkey_stop():
                try:
                    # Pausa inspelning när tangenterna släpps (fortsätt samla)
                    if self.hotkey_recording:
                        print("Push-to-talk: Pausar inspelning")
                        self.hotkey_recording = False
                        if self.is_recording and not self.is_paused:
                            self.root.after(0, self.pause_recording)
                except Exception as e:
                    print(f"Hotkey stop-fel: {e}")
            
            # Starta listener i separat tråd
            def start_listener():
                try:
                    # Högerpil + Shift kombinationshemtning
                    with keyboard.Listener(
                        on_press=self.on_key_press,
                        on_release=self.on_key_release
                    ) as listener:
                        self.hotkey_listener = listener
                        self.hotkey_pressed = {'shift_r': False, 'right': False}
                        self.hotkey_start_callback = on_hotkey_start
                        self.hotkey_stop_callback = on_hotkey_stop
                        listener.join()
                except Exception as e:
                    print(f"Listener-fel: {e}")
            
            threading.Thread(target=start_listener, daemon=True).start()
            print("Global hotkey konfigurerad: Höger Shift + Högerpil (push-to-talk)")
                
        except ImportError:
            print("pynput ej installerat - global hotkey ej tillgänglig")
        except Exception as e:
            print(f"Kunde inte sätta upp global hotkey: {e}")
    
    def on_key_press(self, key):
        """Hantera key press för global hotkey - höger shift + högerpil"""
        try:
            from pynput import keyboard
            if key == keyboard.Key.shift_r:  # Specifikt höger shift
                self.hotkey_pressed['shift_r'] = True
            elif key == keyboard.Key.right:
                self.hotkey_pressed['right'] = True
            
            # Kontrollera om båda tangenterna är nedtryckta
            if self.hotkey_pressed['shift_r'] and self.hotkey_pressed['right']:
                self.hotkey_start_callback()
                
        except Exception as e:
            pass  # Dölj fel för mindre spam
    
    def on_key_release(self, key):
        """Hantera key release för global hotkey"""
        try:
            from pynput import keyboard
            if key == keyboard.Key.shift_r:  # Specifikt höger shift
                self.hotkey_pressed['shift_r'] = False
                # Stoppa inspelning om någon av tangenterna släpps
                if self.hotkey_recording:
                    self.hotkey_stop_callback()
            elif key == keyboard.Key.right:
                self.hotkey_pressed['right'] = False
                # Stoppa inspelning om någon av tangenterna släpps
                if self.hotkey_recording:
                    self.hotkey_stop_callback()
        except Exception as e:
            pass  # Dölj fel för mindre spam
    
    def bind_hover_events(self):
        """Bind hover events till alla widgets för bättre coverage"""
        def bind_to_widget(widget):
            widget.bind('<Enter>', self.on_hover_enter)
            widget.bind('<Leave>', self.on_hover_leave)
            for child in widget.winfo_children():
                bind_to_widget(child)
        
        bind_to_widget(self.root)
        
    def run(self):
        try:
            self.root.mainloop()
        finally:
            # Städa upp vid stängning
            self.cleanup()
    
    def cleanup(self):
        """Städa upp resurser vid stängning"""
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except:
                pass
        
        # Ta bort temp-fil
        if self.audio_file_path and os.path.exists(self.audio_file_path):
            try:
                os.remove(self.audio_file_path)
            except:
                pass

if __name__ == "__main__":
    app = Diktafon()
    app.run()