import os
from moviepy.editor import VideoFileClip

def elabora_cartella_video_finale(path_cartella_originale, durata_taglio=30):
    # 1. Crea il nome della nuova cartella
    path_cartella_originale = path_cartella_originale.rstrip(os.sep)
    nuova_cartella = f"{path_cartella_originale}_taglio_finale"

    # 2. Crea la cartella se non esiste
    if not os.path.exists(nuova_cartella):
        os.makedirs(nuova_cartella)
        print(f"Cartella creata: {nuova_cartella}")

    # 3. Estensioni video comuni da processare
    estensioni_valide = ('.mp4', '.avi', '.mov', '.mkv', '.wmv')

    # 4. Ciclo attraverso i file della cartella originale
    for nome_file in os.listdir(path_cartella_originale):
        if nome_file.lower().endswith(estensioni_valide):
            input_path = os.path.join(path_cartella_originale, nome_file)
            
            # Crea il nome del file di output
            nome_base, estensione = os.path.splitext(nome_file)
            output_path = os.path.join(nuova_cartella, f"{nome_base}_finale{estensione}")

            try:
                print(f"\n--- Elaborazione: {nome_file} ---")
                video = VideoFileClip(input_path)
                durata_totale = video.duration
                
                # IL TAGLIO PARTE DALLA FINE (ultimi 30 secondi)
                start_time = max(0, durata_totale - durata_taglio)
                end_time = durata_totale
                
                # Esegue il taglio
                nuovo_video = video.subclip(start_time, end_time)
                
                # Scrittura del file nella NUOVA cartella
                nuovo_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
                
                # Chiude i file per liberare risorse
                video.close()
                nuovo_video.close()
                
            except Exception as e:
                print(f"Errore durante l'elaborazione di {nome_file}: {e}")

    print("\nProcesso completato per tutti i video (Taglio Finale).")

# Esempio di utilizzo:
if __name__ == "__main__":
    percorso_input = "C:/Users/arion/Desktop/Tirocinio_AI_Pyt/fe/WPy64-31180/Video/CONTROLLI/records"
    elabora_cartella_video_finale(percorso_input)
