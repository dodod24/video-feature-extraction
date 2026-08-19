import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Analisi')))
from comparazione_modelli import esegui_comparazione_modelli

def crea_tab_comparazione(parent, text_log):
    file_meta_base = tk.StringVar()
    file_meta_base_disp = tk.StringVar(value="Nessun file selezionato")
    file_meta_adv = tk.StringVar()
    file_meta_adv_disp = tk.StringVar(value="Nessun file selezionato")
    cartella_meta_out = tk.StringVar()
    cartella_meta_out_disp = tk.StringVar(value="Nessuna cartella selezionata")
    nome_meta_out = tk.StringVar(value="Report_Meta_Analisi")

    def scegli_meta_base():
        f = filedialog.askopenfilename(title="Seleziona File Base", filetypes=[("File Dati", "*.xlsx *.json")])
        if f:
            file_meta_base.set(f)
            file_meta_base_disp.set(os.path.basename(f))
    
    def scegli_meta_adv():
        f = filedialog.askopenfilename(title="Seleziona File Avanzato", filetypes=[("File Dati", "*.xlsx *.json")])
        if f:
            file_meta_adv.set(f)
            file_meta_adv_disp.set(os.path.basename(f))
            
    def scegli_meta_output():
        d = filedialog.askdirectory(title="Seleziona cartella di salvataggio")
        if d:
            cartella_meta_out.set(d)
            cartella_meta_out_disp.set(os.path.basename(d))
            
    def esegui_meta():
        if not file_meta_base.get() or not file_meta_adv.get() or not cartella_meta_out.get():
            messagebox.showwarning("Attenzione", "Seleziona entrambi i file e la cartella di output.")
            return
            
        btn_avvia_meta.config(state="disabled")
        text_log.configure(state="normal")
        text_log.delete(1.0, tk.END)
        text_log.configure(state="disabled")
        
        def thread_meta():
            try:
                nome_base = nome_meta_out.get().strip() or "Report_Meta_Analisi"
                successo = esegui_comparazione_modelli(file_meta_base.get(), file_meta_adv.get(), cartella_meta_out.get(), nome_base)
                if successo:
                    messagebox.showinfo("Completato", "Meta-Analisi completata con successo! Controlla la cartella di output.")
            except Exception as e:
                print(f"\n Errore imprevisto: {e}")
            finally:
                btn_avvia_meta.config(state="normal")
                
        threading.Thread(target=thread_meta, daemon=True).start()

    frame_meta_base = tk.LabelFrame(parent, text="1. Risultati Modello Base (Senza Metriche)", font=("Arial", 10, "bold"), padx=10, pady=10)
    frame_meta_base.pack(fill="x", padx=20, pady=15)
    tk.Button(frame_meta_base, text="Seleziona Excel Base", command=scegli_meta_base, width=25).pack(side=tk.LEFT, padx=5)
    tk.Label(frame_meta_base, textvariable=file_meta_base_disp, fg="blue", wraplength=500, justify="left").pack(side=tk.LEFT, padx=5)
    
    frame_meta_adv = tk.LabelFrame(parent, text="2. Risultati Modello Avanzato (Con EAR/MAR/Smoothing)", font=("Arial", 10, "bold"), padx=10, pady=10)
    frame_meta_adv.pack(fill="x", padx=20, pady=15)
    tk.Button(frame_meta_adv, text="Seleziona Excel Avanzato", command=scegli_meta_adv, width=25).pack(side=tk.LEFT, padx=5)
    tk.Label(frame_meta_adv, textvariable=file_meta_adv_disp, fg="blue", wraplength=500, justify="left").pack(side=tk.LEFT, padx=5)
    
    frame_meta_out = tk.LabelFrame(parent, text="3. Salvataggio Report di Comparazione", font=("Arial", 10, "bold"), padx=10, pady=10)
    frame_meta_out.pack(fill="x", padx=20, pady=15)
    frame_mdir = tk.Frame(frame_meta_out)
    frame_mdir.pack(fill="x", pady=2)
    tk.Button(frame_mdir, text="Seleziona Cartella", command=scegli_meta_output, width=25).pack(side=tk.LEFT, padx=5)
    tk.Label(frame_mdir, textvariable=cartella_meta_out_disp, fg="blue", wraplength=500, justify="left").pack(side=tk.LEFT, padx=5)
    frame_mnome = tk.Frame(frame_meta_out)
    frame_mnome.pack(fill="x", pady=5)
    tk.Label(frame_mnome, text="Nome Base File (Senza Estensione):", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
    tk.Entry(frame_mnome, textvariable=nome_meta_out, width=40).pack(side=tk.LEFT, padx=5)
    
    btn_avvia_meta = tk.Button(parent, text="AVVIA META-ANALISI", font=("Arial", 12, "bold"), bg="#e67e22", fg="white", command=esegui_meta, pady=5)
    btn_avvia_meta.pack(pady=20)
