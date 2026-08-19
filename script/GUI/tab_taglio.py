import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
import threading
import sys
import os

# Assicuriamoci che python trovi la cartella "taglio" che si trova allo stesso livello di "GUI"
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importiamo le funzioni di taglio
try:
    from taglio.taglio_video import elabora_cartella_video as taglio_centrale
    from taglio.taglio_video_iniziale import elabora_cartella_video_iniziale as taglio_iniziale
    from taglio.taglio_video_finale import elabora_cartella_video_finale as taglio_finale
except ImportError as e:
    print(f"Attenzione: Moduli di taglio non trovati o incompleti. Errore: {e}")

def crea_tab_taglio(parent_frame):
    tk.Label(parent_frame, text="FASE 1: TAGLIO E PREPARAZIONE VIDEO", font=("Arial", 12, "bold")).pack(pady=(10, 5))
    tk.Label(parent_frame, text="Taglia i video originali in segmenti clinici (iniziale, centrale o finale) per ridurre il rumore.").pack(pady=(0, 10))

    # --- Sezione Cartella ---
    frame_cartella = tk.LabelFrame(parent_frame, text="1. Cartella Video Originali", font=("Arial", 10, "bold"), padx=10, pady=10)
    frame_cartella.pack(fill="x", padx=20, pady=10)

    var_cartella_input = tk.StringVar(value="Nessuna cartella selezionata")
    full_cartella_path = tk.StringVar()

    def seleziona_cartella():
        directory = filedialog.askdirectory(title="Seleziona la cartella con i video originali")
        if directory:
            full_cartella_path.set(directory)
            var_cartella_input.set(os.path.basename(directory))

    tk.Button(frame_cartella, text="Scegli Cartella", command=seleziona_cartella, width=15).grid(row=5, column=0, sticky="w", pady=10)
    tk.Label(frame_cartella, textvariable=var_cartella_input, fg="blue").grid(row=5, column=0, sticky="w", padx=(130, 0), pady=10)

    # La sezione opzioni è stata unita a frame_cartella per una griglia più pulita
    var_tipo_taglio = tk.StringVar(value="iniziale")

    tk.Label(frame_cartella, text="Modalità di taglio:").grid(row=0, column=0, sticky="w", pady=5)
    
    rb_iniziale = tk.Radiobutton(frame_cartella, text="Taglio Iniziale (Primi secondi - Es. fase di accoglienza)", variable=var_tipo_taglio, value="iniziale")
    rb_iniziale.grid(row=1, column=0, sticky="w", pady=2)
    
    rb_centrale = tk.Radiobutton(frame_cartella, text="Taglio Centrale (Secondi centrali - Estratti da metà video)", variable=var_tipo_taglio, value="centrale")
    rb_centrale.grid(row=2, column=0, sticky="w", pady=2)
    
    rb_finale = tk.Radiobutton(frame_cartella, text="Taglio Finale (Ultimi secondi - Es. fase di rilassamento)", variable=var_tipo_taglio, value="finale")
    rb_finale.grid(row=3, column=0, sticky="w", pady=2)

    tk.Label(frame_cartella, text="Durata segmento (secondi):").grid(row=4, column=0, sticky="w", pady=(10, 2))
    
    var_durata = tk.IntVar(value=30)
    spin_durata = tk.Spinbox(frame_cartella, from_=5, to=600, textvariable=var_durata, width=10)
    spin_durata.grid(row=4, column=0, sticky="w", padx=(180, 0), pady=(10, 2))

    # --- Pulsante Avvia ---
    frame_azione = tk.Frame(parent_frame)
    frame_azione.pack(fill="x", padx=20, pady=20)

    def avvia_elaborazione():
        cartella = full_cartella_path.get()
        if not cartella:
            messagebox.showwarning("Attenzione", "Seleziona prima la cartella dei video!")
            return
            
        try:
            durata = var_durata.get()
        except Exception:
            messagebox.showerror("Errore", "La durata deve essere un numero intero valido.")
            return
            
        tipo = var_tipo_taglio.get()
        
        btn_avvia.config(state="disabled")
        print("\n" + "="*60)
        print(" AVVIO TAGLIO VIDEO")
        print("="*60)
        print(f"Cartella: {cartella}")
        print(f"Modalità: {tipo.upper()}")
        print(f"Durata: {durata} secondi")
        print("Attendere il completamento dell'operazione...")
        
        def run_thread():
            try:
                if tipo == "iniziale":
                    taglio_iniziale(cartella, durata_taglio=durata)
                elif tipo == "centrale":
                    taglio_centrale(cartella, durata_taglio=durata)
                elif tipo == "finale":
                    taglio_finale(cartella, durata_taglio=durata)
            except Exception as e:
                print(f"\nERRORE CRITICO durante il taglio: {e}")
            finally:
                btn_avvia.config(state="normal")
                print("\nPuoi procedere al Tab 2 per l'Estrazione Dati sui video tagliati.")

        threading.Thread(target=run_thread, daemon=True).start()

    btn_avvia = tk.Button(frame_azione, text=" AVVIA TAGLIO VIDEO ", font=("Arial", 12, "bold"), bg="#e67e22", fg="white", height=2, command=avvia_elaborazione)
    btn_avvia.pack(fill="x")
