import os
import re
import pandas as pd
from feat import Detector

# Importiamo la logica geometrica dal nuovo script
from metriche_geometriche import calculate_ear, calculate_mar

def extract_id_from_filename(filename):
    match = re.search(r'^._(.*?)(?=_20\d{2})', filename)
    if match:
        return match.group(1)
    parts = filename.split('_')
    if len(parts) > 3:
        return f"{parts[1]}_{parts[2]}_{parts[3]}"
    return "ID_Sconosciuto"

def process_videos_realtime(video_paths, output_excel, output_json, extract_ear=False, extract_mar=False, apply_smoothing=False):
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
    
    if not video_paths:
        print("ATTENZIONE: Nessun video fornito per l'analisi.")
        return

    print("=" * 60)
    print(" AVVIO PROCESSO DI ANALISI")
    print("=" * 60)
    print(f"Totale video da elaborare: {len(video_paths)}")
    print("-" * 60)

    for index, video_path in enumerate(video_paths):
        video_file = os.path.basename(video_path)
        video_id = extract_id_from_filename(video_file)
        
        print(f"\n[{index + 1}/{len(video_paths)}] Analisi in corso per: {video_id} ({video_file})")
        
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

                # PULIZIA DEL RUMORE (Data Smoothing)
                if apply_smoothing:
                    au_cols = [c for c in valid_preds.columns if 'AU' in c]
                    if au_cols:
                        # Applica un filtro mediano a finestra mobile per eliminare lo sfarfallio
                        valid_preds[au_cols] = valid_preds[au_cols].rolling(window=5, min_periods=1, center=True).median()

                # 4. ESTRAZIONE STATISTICA AU: Media + Picchi (Max) + Varianza (Std)
                mean_aus = valid_preds.aus.mean().add_prefix('Mean_')
                max_aus = valid_preds.aus.max().add_prefix('Max_') # Trova l'intensità massima dell'AU
                std_aus = valid_preds.aus.std().fillna(0).add_prefix('Std_') # Varianza: misura la rigidità/dinamicità
                
                # 5. METRICHE GEOMETRICHE: Head Pose (Pitch, Yaw, Roll)
                try:
                    if hasattr(valid_preds, 'poses'):
                        pose_data = valid_preds.poses
                    else:
                        pose_cols = [c for c in valid_preds.columns if c.lower() in ['pitch', 'yaw', 'roll']]
                        pose_data = valid_preds[pose_cols]
                    
                    mean_pose = pose_data.mean().add_prefix('Mean_')
                    std_pose = pose_data.std().fillna(0).add_prefix('Std_')
                except Exception:
                    mean_pose = pd.Series(dtype=float)
                    std_pose = pd.Series(dtype=float)

                # 6. METRICHE GEOMETRICHE: Apertura Occhi (Eye Aspect Ratio - EAR)
                ear_stats = {}
                if extract_ear:
                    ear_values = []
                    for idx, r in valid_preds.iterrows():
                        try:
                            # Cerca colonne landmarks x_36, y_36 ecc. (68 punti standard)
                            l_eye = [(r[f'x_{i}'], r[f'y_{i}']) for i in range(36, 42)]
                            r_eye = [(r[f'x_{i}'], r[f'y_{i}']) for i in range(42, 48)]
                            ear_left = calculate_ear(l_eye)
                            ear_right = calculate_ear(r_eye)
                            ear_values.append((ear_left + ear_right) / 2.0)
                        except KeyError:
                            pass # Landmarks non trovati
                    
                    if ear_values:
                        ear_series = pd.Series(ear_values)
                        ear_stats['Mean_EAR'] = ear_series.mean()
                        ear_stats['Std_EAR'] = ear_series.std()
                        if pd.isna(ear_stats['Std_EAR']): ear_stats['Std_EAR'] = 0.0

                # 7. METRICHE GEOMETRICHE: Apertura Bocca (Mouth Aspect Ratio - MAR)
                mar_stats = {}
                if extract_mar:
                    mar_values = []
                    for idx, r in valid_preds.iterrows():
                        try:
                            # Cerca colonne landmarks x_48, y_48 ecc. (bocca 48-59)
                            mouth = [(r[f'x_{i}'], r[f'y_{i}']) for i in range(48, 60)]
                            mar_val = calculate_mar(mouth)
                            mar_values.append(mar_val)
                        except KeyError:
                            pass
                    
                    if mar_values:
                        mar_series = pd.Series(mar_values)
                        mar_stats['Mean_MAR'] = mar_series.mean()
                        mar_stats['Std_MAR'] = mar_series.std()
                        if pd.isna(mar_stats['Std_MAR']): mar_stats['Std_MAR'] = 0.0

                mean_emotions = valid_preds.emotions.mean()
                dominant_emotion = mean_emotions.idxmax()
                
                # Creazione riga
                row = {
                    "ID_Soggetto": video_id,
                    "Emozione_Prevalente": dominant_emotion,
                    "Nome_File": video_file
                }
                
                # Uniamo tutti i dati statistici nel dizionario
                row.update(mean_aus.to_dict())
                row.update(max_aus.to_dict())
                row.update(std_aus.to_dict())
                if not mean_pose.empty:
                    row.update(mean_pose.to_dict())
                    row.update(std_pose.to_dict())
                if ear_stats:
                    row.update(ear_stats)
                if mar_stats:
                    row.update(mar_stats)
                
                summary_data.append(row)
                
                df_temp = pd.DataFrame(summary_data)
                
                cols = ["ID_Soggetto", "Emozione_Prevalente", "Nome_File"]
                other_cols = [c for c in df_temp.columns if c not in cols]
                df_temp = df_temp[cols + other_cols]
                
                df_temp.to_excel(output_excel, index=False)
                df_temp.to_json(output_json, orient="records", indent=4)
                
                print(f"      > Estrazione dati e metriche completata.")
            else:
                print(f"      > ATTENZIONE: Nessun volto rilevato in questo video. Salto.")

        except Exception as e:
            print(f"      > ERRORE durante l'elaborazione: {e}")

    print("\n" + "=" * 60)
    print(" ELABORAZIONE TERMINATA CON SUCCESSO")
    print("=" * 60)
    print(f"File Excel salvato in: {output_excel}")
    print(f"File JSON salvato in: {output_json}\n")

if __name__ == "__main__":
    print("Questo script contiene solo la logica di analisi. Esegui 'main_gui.py' per usare l'interfaccia grafica.")