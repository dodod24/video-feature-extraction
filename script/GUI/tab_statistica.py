import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Analisi')))
from analisi_statistica import esegui_analisi_statistica

def crea_tab_statistica(parent, text_log):
    file_dataset1 = tk.StringVar()
    file_dataset1_disp = tk.StringVar(value="Nessun file selezionato")
    file_dataset2 = tk.StringVar()
    file_dataset2_disp = tk.StringVar(value="Nessun file selezionato")
    cartella_out = tk.StringVar()
    cartella_out_disp = tk.StringVar(value="Nessuna cartella selezionata")
    filtro_var = tk.StringVar(value="all")
    nome_out = tk.StringVar(value="Risultati_Comparativi")

    def scegli_dataset1():
        f = filedialog.askopenfilename(title="Seleziona il Dataset 1", filetypes=[("File Dati", "*.xlsx *.json"), ("Tutti i file", "*.*")])
        if f:
            file_dataset1.set(f)
            file_dataset1_disp.set(os.path.basename(f))
            
    def scegli_dataset2():
        f = filedialog.askopenfilename(title="Seleziona il Dataset 2", filetypes=[("File Dati", "*.xlsx *.json"), ("Tutti i file", "*.*")])
        if f:
            file_dataset2.set(f)
            file_dataset2_disp.set(os.path.basename(f))
            
    def scegli_output():
        d = filedialog.askdirectory(title="Seleziona la cartella di salvataggio")
        if d:
            cartella_out.set(d)
            cartella_out_disp.set(os.path.basename(d))
            
    def esegui():
        if not file_dataset1.get() or not file_dataset2.get() or not cartella_out.get():
            messagebox.showwarning("Attenzione", "Seleziona entrambi i dataset e la cartella di output.")
            return
            
        ext_ds1 = os.path.splitext(file_dataset1.get())[1].lower()
        ext_ds2 = os.path.splitext(file_dataset2.get())[1].lower()
        
        if ext_ds1 != ext_ds2:
            messagebox.showerror("Errore di Formato", "I due file Dataset devono avere lo stesso formato (entrambi .xlsx o entrambi .json).")
            return
            
        btn_avvia.config(state="disabled")
        text_log.configure(state="normal")
        text_log.delete(1.0, tk.END)
        text_log.configure(state="disabled")
        
        def thread_task():
            try:
                nome_base = nome_out.get().strip() or "Risultati"
                successo = esegui_analisi_statistica(file_dataset1.get(), file_dataset2.get(), cartella_out.get(), filtro_var.get(), nome_base)
                if successo:
                    messagebox.showinfo("Completato", "Analisi statistica completata con successo! Controlla la cartella di output.")
            except Exception as e:
                print(f"\n Errore imprevisto: {e}")
            finally:
                btn_avvia.config(state="normal")
                
        threading.Thread(target=thread_task, daemon=True).start()

    frame_ds1 = tk.LabelFrame(parent, text="1. Primo File", font=("Arial", 10, "bold"), padx=10, pady=5)
    frame_ds1.pack(fill="x", padx=20, pady=10)
    tk.Button(frame_ds1, text="Seleziona Dataset 1", command=scegli_dataset1, width=25).pack(side=tk.LEFT, padx=5)
    tk.Label(frame_ds1, textvariable=file_dataset1_disp, fg="blue", wraplength=500, justify="left").pack(side=tk.LEFT, padx=5)
    
    frame_ds2 = tk.LabelFrame(parent, text="2. Secondo File", font=("Arial", 10, "bold"), padx=10, pady=5)
    frame_ds2.pack(fill="x", padx=20, pady=10)
    tk.Button(frame_ds2, text="Seleziona Dataset 2", command=scegli_dataset2, width=25).pack(side=tk.LEFT, padx=5)
    tk.Label(frame_ds2, textvariable=file_dataset2_disp, fg="blue", wraplength=500, justify="left").pack(side=tk.LEFT, padx=5)
    
    frame_out = tk.LabelFrame(parent, text="3. Salvataggio Risultati", font=("Arial", 10, "bold"), padx=10, pady=5)
    frame_out.pack(fill="x", padx=20, pady=10)
    frame_dir = tk.Frame(frame_out)
    frame_dir.pack(fill="x", pady=2)
    tk.Button(frame_dir, text="Seleziona Cartella", command=scegli_output, width=25).pack(side=tk.LEFT, padx=5)
    tk.Label(frame_dir, textvariable=cartella_out_disp, fg="blue", wraplength=500, justify="left").pack(side=tk.LEFT, padx=5)
    
    frame_nome = tk.Frame(frame_out)
    frame_nome.pack(fill="x", pady=5)
    tk.Label(frame_nome, text="Nome Base File (Senza Estensione):", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
    tk.Entry(frame_nome, textvariable=nome_out, width=40).pack(side=tk.LEFT, padx=5)
    
    frame_opt = tk.LabelFrame(parent, text="4. Filtro Analisi (Meno variabili = meno falsi negativi FDR)", font=("Arial", 10, "bold"), padx=10, pady=5)
    frame_opt.pack(fill="x", padx=20, pady=10)
    tk.Radiobutton(frame_opt, text="Analizza TUTTE le metriche (Mean, Std, Max)", variable=filtro_var, value="all").pack(anchor="w")
    tk.Radiobutton(frame_opt, text="Analizza SOLO le Medie (Mean_)", variable=filtro_var, value="mean").pack(anchor="w")
    tk.Radiobutton(frame_opt, text="Analizza SOLO le Varianze (Std_)", variable=filtro_var, value="std").pack(anchor="w")
    
    btn_avvia = tk.Button(parent, text="AVVIA ANALISI STATISTICA", font=("Arial", 12, "bold"), bg="#e67e22", fg="white", command=esegui, pady=5)
    btn_avvia.pack(pady=15)
