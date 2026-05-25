import os
import re
import pandas as pd
from feat import Detector

def extract_id_from_filename(filename):
    match = re.search(r'^._(.*?)(?=_20\d{2})', filename)
    if match:
        return match.group(1)
    parts = filename.split('_')
    if len(parts) > 3:
        return f"{parts[1]}_{parts[2]}_{parts[3]}"
    return "ID_Sconosciuto"

def process_videos_realtime(video_folder, output_excel, output_json):
    # 1. MODELLI: Proviamo 'rf' (Random Forest) per le AU, spesso più robusto di SVM.
    # Mantieni 'svm' se 'rf' ti dà errori di libreria mancante.
    detector = Detector(
        face_model="retinaface",
        landmark_model="mobilefacenet",
        au_model="xgb", 
        emotion_model="resmasknet",
        device="cuda"
    )

    summary_data = []
    video_extensions = ('.mp4', '.avi', '.mov', '.mkv')
    video_files = [f for f in os.listdir(video_folder) if f.lower().endswith(video_extensions)]

    if not video_files:
        print(f"⚠️ Nessun video trovato: {video_folder}")
        return

    print(f"📂 Trovati {len(video_files)} video. Inizio analisi ad alta precisione...")

    for index, video_file in enumerate(video_files):
        video_id = extract_id_from_filename(video_file)
        video_path = os.path.join(video_folder, video_file)
        
        print(f"\n[{index + 1}/{len(video_files)}] 🔍 Analisi in corso: {video_id}...")
        
        try:
            # 2. CAMPIONAMENTO: skip_frames=2 (o 1 se hai molto tempo a disposizione)
            # per non perdere le micro-espressioni rapide.
            predictions = detector.detect_video(video_path, skip_frames=2)
            
            if predictions is not None and not predictions.empty:
                
                # 3. FILTRO QUALITÀ: Rimuoviamo i frame in cui la detection del volto è incerta
                # Py-Feat usa comunemente 'FaceScore' o 'face_score' (adatto ad entrambe le nomenclature)
                score_col = 'FaceScore' if 'FaceScore' in predictions.columns else 'face_score' if 'face_score' in predictions.columns else None
                
                if score_col:
                    valid_preds = predictions[predictions[score_col] > 0.8]
                    # Se il filtro elimina tutti i frame, facciamo fallback sui dati originali
                    if valid_preds.empty:
                        valid_preds = predictions
                else:
                    valid_preds = predictions

                # 4. ESTRAZIONE STATISTICA: Media + Picchi (Max)
                mean_aus = valid_preds.aus.mean().add_prefix('Mean_')
                max_aus = valid_preds.aus.max().add_prefix('Max_') # Trova l'intensità massima dell'AU
                
                mean_emotions = valid_preds.emotions.mean()
                dominant_emotion = mean_emotions.idxmax()
                
                # Creazione riga
                row = {
                    "ID_Soggetto": video_id,
                    "Emozione_Prevalente": dominant_emotion,
                    "Nome_File": video_file
                }
                
                # Uniamo le medie e i valori massimi nel dizionario
                row.update(mean_aus.to_dict())
                row.update(max_aus.to_dict())
                
                summary_data.append(row)
                
                df_temp = pd.DataFrame(summary_data)
                
                cols = ["ID_Soggetto", "Emozione_Prevalente", "Nome_File"]
                other_cols = [c for c in df_temp.columns if c not in cols]
                df_temp = df_temp[cols + other_cols]
                
                df_temp.to_excel(output_excel, index=False)
                df_temp.to_json(output_json, orient="records", indent=4)
                
                print(f"✅ Dati di {video_id} salvati (Media e Picchi registrati).")
            else:
                print(f"❓ Nessun volto rilevato nel video {video_file}. Salto...")

        except Exception as e:
            print(f"❌ Errore durante l'elaborazione di {video_file}: {e}")

    print(f"\n🎯 Processo terminato! I file finali sono:\n- {output_excel}\n- {output_json}")

if __name__ == "__main__":
    CARTELLA_VIDEO = "C:/Users/dodod/WPy64-31180/VIDEO/videotagli" 
    NOME_REPORT_EXCEL = "Analisi_AU_AltaPrecisione.xlsx"
    NOME_REPORT_JSON = "Analisi_AU_AltaPrecisione.json"

    process_videos_realtime(CARTELLA_VIDEO, NOME_REPORT_EXCEL, NOME_REPORT_JSON)