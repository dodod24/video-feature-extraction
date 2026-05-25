import os
from moviepy.editor import VideoFileClip

def elabora_cartella_video(path_cartella_originale, durata_taglio=30):
    # 1. Crea il nome della nuova cartella (es: "Video" -> "Video_taglio")
    # Rimuove eventuali slash finali per evitare errori nel nome
    path_cartella_originale = path_cartella_originale.rstrip(os.sep)
    nuova_cartella = f"{path_cartella_originale}_taglio"

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
            
            # Crea il nome del file di output con il suffisso "_taglio"
            nome_base, estensione = os.path.splitext(nome_file)
            output_path = os.path.join(nuova_cartella, f"{nome_base}_taglio{estensione}")

            try:
                print(f"\n--- Elaborazione: {nome_file} ---")
                video = VideoFileClip(input_path)
                durata_totale = video.duration
                
                # Il taglio parte a metÃ  del video
                start_time = durata_totale / 2
                end_time = min(durata_totale, start_time + durata_taglio)
                
                # Esegue il taglio
                nuovo_video = video.subclip(start_time, end_time)
                
                # Scrittura del file nella NUOVA cartella
                nuovo_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
                
                # Chiude i file per liberare risorse
                video.close()
                nuovo_video.close()
                
            except Exception as e:
                print(f"Errore durante l'elaborazione di {nome_file}: {e}")

    print("\nProcesso completato per tutti i video.")

# Esempio di utilizzo:
# Inserisci qui il percorso della tua cartella (es: "C:/Video/MieiVideo" o semplicemente "MieiVideo")
percorso_input = "C:/Users/dodod/WPy64-31180/VIDEO/CONTROLLI"
elabora_cartella_video(percorso_input)