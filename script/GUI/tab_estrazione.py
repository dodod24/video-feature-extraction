import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Analisi')))
from analisi_estrazione_video import process_videos_realtime

def crea_tab_estrazione(parent, text_log):
    input_paths = []
    output_dir = tk.StringVar()
    output_dir_disp = tk.StringVar(value="Nessuna cartella selezionata")
    base_name = tk.StringVar(value="Analisi_Video")
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
                print(f"\nErrore imprevisto durante l'analisi: {e}")
            finally:
                btn_avvia.config(state="normal")
        
        threading.Thread(target=thread_task, daemon=True).start()

    frame_input = tk.LabelFrame(parent, text="1. Scegli cosa analizzare:", font=("Arial", 10, "bold"), padx=10, pady=5)
    frame_input.pack(fill="x", pady=5, padx=20)
    tk.Button(frame_input, text="Seleziona Singolo Video", command=seleziona_video_singolo).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_input, text="Seleziona Intera Cartella", command=seleziona_cartella_video).pack(side=tk.LEFT, padx=5)
    
    lbl_input_sel = tk.Label(frame_input, text="Nessun video selezionato", fg="blue")
    lbl_input_sel.pack(side=tk.LEFT, padx=10)

    frame_out = tk.LabelFrame(parent, text="2. Scegli dove salvare i risultati JSON e Excel:", font=("Arial", 10, "bold"), padx=10, pady=5)
    frame_out.pack(fill="x", pady=5, padx=20)
    tk.Button(frame_out, text="Seleziona Cartella Output", command=seleziona_output).pack(side=tk.LEFT, padx=5)
    tk.Label(frame_out, textvariable=output_dir_disp, fg="blue").pack(side=tk.LEFT, padx=5)

    frame_nome = tk.LabelFrame(parent, text="3. Nome base dei file generati:", font=("Arial", 10, "bold"), padx=10, pady=5)
    frame_nome.pack(fill="x", pady=5, padx=20)
    tk.Entry(frame_nome, textvariable=base_name, width=40).pack(pady=2, anchor="w")

    frame_options = tk.LabelFrame(parent, text="4. Metriche Avanzate e Pulizia (Consigliate)", font=("Arial", 10, "bold"), padx=10, pady=10)
    frame_options.pack(pady=15, fill="x", padx=20)
    
    tk.Checkbutton(frame_options, text="Estrai EAR (Dinamica di apertura occhi)", variable=extract_ear_var).pack(anchor="w", pady=2)
    tk.Checkbutton(frame_options, text="Estrai MAR (Dinamica di apertura bocca)", variable=extract_mar_var).pack(anchor="w", pady=2)
    tk.Checkbutton(frame_options, text="Applica Smoothing (Filtro per ridurre il rumore e sfarfallio delle AU)", variable=apply_smoothing_var).pack(anchor="w", pady=2)

    btn_avvia = tk.Button(parent, text="AVVIA ESTRAZIONE DATI DAI VIDEO", font=("Arial", 12, "bold"), bg="#e67e22", fg="white", command=esegui_analisi)
    btn_avvia.pack(pady=15)
