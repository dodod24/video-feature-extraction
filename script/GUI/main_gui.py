import tkinter as tk
import tkinter.ttk as ttk
import sys

from tab_estrazione import crea_tab_estrazione
from tab_statistica import crea_tab_statistica
from tab_comparazione import crea_tab_comparazione
from tab_taglio import crea_tab_taglio

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

def avvia_gui_principale():
    root = tk.Tk()
    root.title("Video Feature Extraction Suite")
    root.geometry("900x750")
    
    # Intestazione
    tk.Label(root, text="INTERFACCIA DI ANALISI VIDEO E COMPARAZIONE STATISTICA", font=("Arial", 14, "bold"), fg="#2c3e50").pack(pady=10)
    
    # Gestore Schede
    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both', padx=10, pady=5)
    
    # Console Condivisa (In Basso)
    frame_console = tk.Frame(root)
    frame_console.pack(fill='x', padx=10, pady=5)
    tk.Label(frame_console, text="Console di Output Condivisa:").pack(anchor="w")
    text_log = tk.Text(frame_console, height=10, state="disabled", bg="#f0f0f0")
    text_log.pack(fill='x')
    
    sys.stdout = TextRedirector(text_log, "stdout")
    sys.stderr = TextRedirector(text_log, "stderr")
    
    # --- Inizializzazione delle 4 Schede ---
    
    # Tab 1: Taglio Video
    tab0 = tk.Frame(notebook)
    notebook.add(tab0, text="1. Taglio Video")
    crea_tab_taglio(tab0)

    # Tab 2: Estrazione Video
    tab1 = tk.Frame(notebook)
    notebook.add(tab1, text="2. Estrazione Dati Video")
    crea_tab_estrazione(tab1, text_log)
    
    # Tab 3: Analisi Statistica
    tab2 = tk.Frame(notebook)
    notebook.add(tab2, text="3. Analisi Statistica")
    crea_tab_statistica(tab2, text_log)
    
    # Tab 4: Confronto Modelli
    tab3 = tk.Frame(notebook)
    notebook.add(tab3, text="4. Confronto Modelli")
    crea_tab_comparazione(tab3, text_log)
    
    root.mainloop()

if __name__ == "__main__":
    avvia_gui_principale()
