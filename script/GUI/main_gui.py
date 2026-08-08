import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

# Aggiungiamo la cartella Analisi al path per poter importare gli script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Analisi')))
from analisi_excl_json import process_videos_realtime

class TextRedirector(object):
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str_text):
        self.widget.configure(state="normal")
        self.widget.insert("end", str_text, (self.tag,))
        self.widget.see("end")
        self.widget.configure(state="disabled")
        self.widget.update_idletasks()

    def flush(self):
        pass

def avvia_gui():
    root = tk.Tk()
    root.title("Analisi Video AU e Emozioni (Py-Feat)")
    root.geometry("600x500")

    input_paths = []
    output_dir = tk.StringVar()
    output_dir_disp = tk.StringVar(value="Nessuna cartella selezionata")
    base_name = tk.StringVar(value="Analisi_AU_AltaPrecisione")
    extract_ear_var = tk.BooleanVar(value=False)
    extract_mar_var = tk.BooleanVar(value=False)
    apply_smoothing_var = tk.BooleanVar(value=False)

    def seleziona_video_singolo():
        file_path = filedialog.askopenfilename(
            title="Seleziona un video",
            filetypes=[("File Video", "*.mp4 *.avi *.mov *.mkv")]
        )
        if file_path:
            input_paths.clear()
            input_paths.append(file_path)
            lbl_input_sel.config(text=f"Selezionato 1 video: {os.path.basename(file_path)}")

    def seleziona_cartella_video():
        folder_path = filedialog.askdirectory(title="Seleziona cartella video")
        if folder_path:
            input_paths.clear()
            video_extensions = ('.mp4', '.avi', '.mov', '.mkv')
            for f in os.listdir(folder_path):
                if f.lower().endswith(video_extensions):
                    input_paths.append(os.path.join(folder_path, f))
            lbl_input_sel.config(text=f"Selezionati {len(input_paths)} video dalla cartella.")

    def seleziona_output():
        folder = filedialog.askdirectory(title="Seleziona cartella di destinazione")
        if folder:
            output_dir.set(folder)
            output_dir_disp.set(os.path.basename(folder))

    def esegui_analisi():
        if not input_paths:
            messagebox.showerror("Errore", "Seleziona prima un video o una cartella!")
            return
        if not output_dir.get():
            messagebox.showerror("Errore", "Seleziona la cartella di destinazione!")
            return
        if not base_name.get():
            messagebox.showerror("Errore", "Inserisci un nome di base per i file!")
            return

        out_excel = os.path.join(output_dir.get(), base_name.get() + ".xlsx")
        out_json = os.path.join(output_dir.get(), base_name.get() + ".json")

        btn_avvia.config(state="disabled")
        text_log.configure(state="normal")
        text_log.delete(1.0, tk.END)
        text_log.configure(state="disabled")
        
        def thread_task():
            try:
                process_videos_realtime(
                    input_paths, 
                    out_excel, 
                    out_json, 
                    extract_ear=extract_ear_var.get(),
                    extract_mar=extract_mar_var.get(),
                    apply_smoothing=apply_smoothing_var.get()
                )
            except Exception as e:
                print(f"\n❌ Errore imprevisto durante l'analisi: {e}")
            finally:
                btn_avvia.config(state="normal")
        
        threading.Thread(target=thread_task, daemon=True).start()

    tk.Label(root, text="1. Scegli cosa analizzare:", font=("Arial", 10, "bold")).pack(pady=(10, 0))
    frame_input = tk.Frame(root)
    frame_input.pack(pady=5)
    tk.Button(frame_input, text="Seleziona Singolo Video", command=seleziona_video_singolo).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_input, text="Seleziona Intera Cartella", command=seleziona_cartella_video).pack(side=tk.LEFT, padx=5)
    
    lbl_input_sel = tk.Label(root, text="Nessun video selezionato", fg="blue")
    lbl_input_sel.pack(pady=2)

    tk.Label(root, text="2. Scegli dove salvare:", font=("Arial", 10, "bold")).pack(pady=(15, 0))
    frame_out = tk.Frame(root)
    frame_out.pack(pady=5)
    tk.Button(frame_out, text="Seleziona Cartella Output", command=seleziona_output).pack(side=tk.LEFT, padx=5)
    tk.Label(frame_out, textvariable=output_dir_disp, fg="blue").pack(side=tk.LEFT, padx=5)

    tk.Label(root, text="3. Nome base dei file generati:", font=("Arial", 10, "bold")).pack(pady=(10, 0))
    tk.Entry(root, textvariable=base_name, width=40).pack(pady=2)

    frame_options = tk.LabelFrame(root, text="4. Metriche Opzionali e Pulizia Dati", font=("Arial", 10, "bold"), padx=10, pady=5)
    frame_options.pack(pady=10, fill="x", padx=20)
    
    tk.Checkbutton(frame_options, text="Estrai EAR (Dinamica di apertura occhi)", variable=extract_ear_var).pack(anchor="w")
    tk.Checkbutton(frame_options, text="Estrai MAR (Dinamica di apertura bocca)", variable=extract_mar_var).pack(anchor="w")
    tk.Checkbutton(frame_options, text="Applica Smoothing (Filtro per ridurre il rumore e sfarfallio delle AU)", variable=apply_smoothing_var).pack(anchor="w")

    btn_avvia = tk.Button(root, text="AVVIA ANALISI", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", command=esegui_analisi)
    btn_avvia.pack(pady=10)

    tk.Label(root, text="Console Output:").pack()
    text_log = tk.Text(root, height=12, width=70, state="disabled", bg="#f0f0f0")
    text_log.pack(padx=10, pady=5)
    
    # Reindirizza print al widget Text
    sys.stdout = TextRedirector(text_log, "stdout")
    sys.stderr = TextRedirector(text_log, "stderr")

    root.mainloop()

if __name__ == "__main__":
    avvia_gui()
