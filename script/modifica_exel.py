import os
import re
import pandas as pd
from feat import Detector

def extract_id_from_filename(filename):
    """Estrae l'ID saltando la prima lettera e l'underscore iniziale."""
    match = re.search(r'^._(.*?)(?=_20\d{2})', filename)
    if match:
        return match.group(1)
    # Fallback se il pattern fallisce
    parts = filename.split('_')
    if len(parts) > 3:
        return f"{parts[1]}_{parts[2]}_{parts[3]}"
    return "ID_Sconosciuto"

def process_videos_realtime(video_folder, output_excel):
    # Inizializzazione Detector con modello SVM (come richiesto dal tuo sistema)
    detector = Detector(
        face_model="retinaface",
        landmark_model="mobilefacenet",
        au_model="svm",
        emotion_model="resmasknet",
        device="cuda"
    )

    summary_data = []
    video_extensions = ('.mp4', '.avi', '.mov', '.mkv')
    
    # Lista i file e filtra per estensione
    video_files = [f for f in os.listdir(video_folder) if f.lower().endswith(video_extensions)]

    if not video_files:
        print(f"⚠️ Nessun video trovato nella cartella: {video_folder}")
        return

    print(f"📂 Trovati {len(video_files)} video. Inizio analisi...")

    for index, video_file in enumerate(video_files):
        video_id = extract_id_from_filename(video_file)
        video_path = os.path.join(video_folder, video_file)
        
        print(f"\n[{index + 1}/{len(video_files)}] 🔍 Analisi in corso: {video_id}...")
        
        try:
            # Analisi con skip_frames=5 (6 analisi al secondo per video a 30fps)
            predictions = detector.detect_video(video_path, skip_frames=5)
            
            if predictions is not None and len(predictions) > 0:
                # Calcolo medie AU ed Emozioni
                mean_aus = predictions.aus.mean()
                mean_emotions = predictions.emotions.mean()
                dominant_emotion = mean_emotions.idxmax()
                
                # Creazione riga
                row = {
                    "ID_Soggetto": video_id,
                    "Emozione_Prevalente": dominant_emotion,
                    "Nome_File": video_file
                }
                row.update(mean_aus.to_dict())
                
                # Aggiunta alla lista principale
                summary_data.append(row)
                
                # --- SALVATAGGIO IN TEMPO REALE ---
                df_temp = pd.DataFrame(summary_data)
                
                # Riordino colonne per avere ID ed Emozione all'inizio
                cols = ["ID_Soggetto", "Emozione_Prevalente", "Nome_File"]
                other_cols = [c for c in df_temp.columns if c not in cols]
                df_temp = df_temp[cols + other_cols]
                
                # Sovrascrive il file Excel ad ogni ciclo
                df_temp.to_excel(output_excel, index=False)
                print(f"✅ Dati di {video_id} salvati correttamente in Excel.")
            else:
                print(f"❓ Nessun volto rilevato nel video {video_file}. Salto...")

        except Exception as e:
            print(f"❌ Errore durante l'elaborazione di {video_file}: {e}")

    print(f"\n🎯 Processo terminato! Il file finale è: {output_excel}")

# --- CONFIGURAZIONE PERCORSI ---
if __name__ == "__main__":
    # Modifica questi percorsi con i tuoi reali
    CARTELLA_VIDEO = "C:/Users/dodod/WPy64-31180/VIDEO/videotagli" 
    NOME_REPORT = "Analisi_AU_RealTime.xlsx"

    process_videos_realtime(CARTELLA_VIDEO, NOME_REPORT)
    