import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
import threading
import sys
import os

# Aggiungiamo la cartella Analisi al path per poter importare gli script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Analisi')))
from analisi_statistica import esegui_analisi_statistica
from comparazione_modelli import esegui_comparazione_modelli

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

def avvia_gui_statistica():
    root = tk.Tk()
    root.title("Suite di Analisi e Comparazione Statistica")
    root.geometry("850x650")
    
    # --- VARIABILI TAB 1 ---
    file_dataset1 = tk.StringVar()
    file_dataset1_disp = tk.StringVar(value="Nessun file selezionato")
    file_dataset2 = tk.StringVar()
    file_dataset2_disp = tk.StringVar(value="Nessun file selezionato")
    cartella_out = tk.StringVar()
    cartella_out_disp = tk.StringVar(value="Nessuna cartella selezionata")
    filtro_var = tk.StringVar(value="all")
    nome_out = tk.StringVar(value="Risultati_Comparativi")
    
    # --- VARIABILI TAB 2 ---
    file_meta_base = tk.StringVar()
    file_meta_base_disp = tk.StringVar(value="Nessun file selezionato")
    file_meta_adv = tk.StringVar()
    file_meta_adv_disp = tk.StringVar(value="Nessun file selezionato")
    cartella_meta_out = tk.StringVar()
    cartella_meta_out_disp = tk.StringVar(value="Nessuna cartella selezionata")
    nome_meta_out = tk.StringVar(value="Report_Meta_Analisi")
    
    # --- FUNZIONI TAB 1 ---
    def scegli_dataset1():
        f = filedialog.askopenfilename(title="Seleziona il Dataset 1 (Excel o JSON)", filetypes=[("File Dati", "*.xlsx *.json"), ("Tutti i file", "*.*")])
        if f:
            file_dataset1.set(f)
            file_dataset1_disp.set(os.path.basename(f))
            
    def scegli_dataset2():
        f = filedialog.askopenfilename(title="Seleziona il Dataset 2 (Excel o JSON)", filetypes=[("File Dati", "*.xlsx *.json"), ("Tutti i file", "*.*")])
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
        
    # --- FUNZIONI TAB 2 ---
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
        
    # ================= UI LAYOUT =================
    tk.Label(root, text="SUITE DI ANALISI E COMPARAZIONE STATISTICA", font=("Arial", 14, "bold"), fg="#2c3e50").pack(pady=10)
    
    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both', padx=10, pady=5)
    
    # --------- TAB 1: Analisi Base ---------
    tab_base = tk.Frame(notebook)
    notebook.add(tab_base, text="1. Analisi Statistica")
    
    frame_ds1 = tk.LabelFrame(tab_base, text="1. Primo File (Dataset 1)", font=("Arial", 10, "bold"), padx=10, pady=5)
    frame_ds1.pack(fill="x", padx=20, pady=5)
    tk.Button(frame_ds1, text="Seleziona Dataset 1", command=scegli_dataset1, width=25).pack(side=tk.LEFT, padx=5)
    tk.Label(frame_ds1, textvariable=file_dataset1_disp, fg="blue", wraplength=500, justify="left").pack(side=tk.LEFT, padx=5)
    
    frame_ds2 = tk.LabelFrame(tab_base, text="2. Secondo File (Dataset 2)", font=("Arial", 10, "bold"), padx=10, pady=5)
    frame_ds2.pack(fill="x", padx=20, pady=5)
    tk.Button(frame_ds2, text="Seleziona Dataset 2", command=scegli_dataset2, width=25).pack(side=tk.LEFT, padx=5)
    tk.Label(frame_ds2, textvariable=file_dataset2_disp, fg="blue", wraplength=500, justify="left").pack(side=tk.LEFT, padx=5)
    
    frame_out = tk.LabelFrame(tab_base, text="3. Salvataggio Risultati", font=("Arial", 10, "bold"), padx=10, pady=5)
    frame_out.pack(fill="x", padx=20, pady=5)
    frame_dir = tk.Frame(frame_out)
    frame_dir.pack(fill="x", pady=2)
    tk.Button(frame_dir, text="Seleziona Cartella", command=scegli_output, width=25).pack(side=tk.LEFT, padx=5)
    tk.Label(frame_dir, textvariable=cartella_out_disp, fg="blue", wraplength=500, justify="left").pack(side=tk.LEFT, padx=5)
    frame_nome = tk.Frame(frame_out)
    frame_nome.pack(fill="x", pady=5)
    tk.Label(frame_nome, text="Nome Base File (Senza Estensione):", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
    tk.Entry(frame_nome, textvariable=nome_out, width=40).pack(side=tk.LEFT, padx=5)
    
    frame_opt = tk.LabelFrame(tab_base, text="4. Filtro Analisi (Meno variabili = meno falsi negativi)", font=("Arial", 10, "bold"), padx=10, pady=5)
    frame_opt.pack(fill="x", padx=20, pady=5)
    tk.Radiobutton(frame_opt, text="Analizza TUTTE le metriche (Mean, Std, Max)", variable=filtro_var, value="all").pack(anchor="w")
    tk.Radiobutton(frame_opt, text="Analizza SOLO le Medie (Mean_)", variable=filtro_var, value="mean").pack(anchor="w")
    tk.Radiobutton(frame_opt, text="Analizza SOLO le Varianze (Std_)", variable=filtro_var, value="std").pack(anchor="w")
    
    btn_avvia = tk.Button(tab_base, text="AVVIA ANALISI STATISTICA", font=("Arial", 12, "bold"), bg="#e67e22", fg="white", command=esegui, pady=5)
    btn_avvia.pack(pady=10)
    
    # --------- TAB 2: Meta-Analisi ---------
    tab_meta = tk.Frame(notebook)
    notebook.add(tab_meta, text="2. Meta-Analisi (Comparazione)")
    
    frame_meta_base = tk.LabelFrame(tab_meta, text="1. Risultati Modello Base (es. Analisi_Senza_Metriche_mean.xlsx)", font=("Arial", 10, "bold"), padx=10, pady=10)
    frame_meta_base.pack(fill="x", padx=20, pady=10)
    tk.Button(frame_meta_base, text="Seleziona Excel Base", command=scegli_meta_base, width=25).pack(side=tk.LEFT, padx=5)
    tk.Label(frame_meta_base, textvariable=file_meta_base_disp, fg="blue", wraplength=500, justify="left").pack(side=tk.LEFT, padx=5)
    
    frame_meta_adv = tk.LabelFrame(tab_meta, text="2. Risultati Modello Avanzato (es. Analisi_Con_Metriche_mean.xlsx)", font=("Arial", 10, "bold"), padx=10, pady=10)
    frame_meta_adv.pack(fill="x", padx=20, pady=10)
    tk.Button(frame_meta_adv, text="Seleziona Excel Avanzato", command=scegli_meta_adv, width=25).pack(side=tk.LEFT, padx=5)
    tk.Label(frame_meta_adv, textvariable=file_meta_adv_disp, fg="blue", wraplength=500, justify="left").pack(side=tk.LEFT, padx=5)
    
    frame_meta_out = tk.LabelFrame(tab_meta, text="3. Salvataggio Report di Comparazione", font=("Arial", 10, "bold"), padx=10, pady=10)
    frame_meta_out.pack(fill="x", padx=20, pady=10)
    frame_mdir = tk.Frame(frame_meta_out)
    frame_mdir.pack(fill="x", pady=2)
    tk.Button(frame_mdir, text="Seleziona Cartella", command=scegli_meta_output, width=25).pack(side=tk.LEFT, padx=5)
    tk.Label(frame_mdir, textvariable=cartella_meta_out_disp, fg="blue", wraplength=500, justify="left").pack(side=tk.LEFT, padx=5)
    frame_mnome = tk.Frame(frame_meta_out)
    frame_mnome.pack(fill="x", pady=5)
    tk.Label(frame_mnome, text="Nome Base File (Senza Estensione):", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
    tk.Entry(frame_mnome, textvariable=nome_meta_out, width=40).pack(side=tk.LEFT, padx=5)
    
    btn_avvia_meta = tk.Button(tab_meta, text="AVVIA META-ANALISI", font=("Arial", 12, "bold"), bg="#e67e22", fg="white", command=esegui_meta, pady=5)
    btn_avvia_meta.pack(pady=15)
    
    # ================= CONSOLE COMUNE =================
    tk.Label(root, text="Console Output:").pack()
    text_log = tk.Text(root, height=10, width=80, state="disabled", bg="#f0f0f0")
    text_log.pack(padx=10, pady=5)
    
    sys.stdout = TextRedirector(text_log, "stdout")
    sys.stderr = TextRedirector(text_log, "stderr")
    
    root.mainloop()

if __name__ == "__main__":
    avvia_gui_statistica()
