import cv2
import matplotlib.pyplot as plt
import pandas as pd
from feat import Detector
import os
import sys
from tqdm import tqdm

def esegui_demo_live(video_path):
    print("⏳ Caricamento dei modelli in VRAM... (Attendere)")
    
    detector = Detector(
        face_model="retinaface",
        landmark_model="mobilefacenet",
        au_model="xgb", 
        emotion_model="resmasknet",
        device="cuda"
    )
    
    print(f"✅ Modelli caricati. Avvio demo per: {os.path.basename(video_path)}")
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("❌ Errore: Impossibile aprire il video.")
        return

    # Otteniamo il numero totale di frame per la barra di caricamento
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    emozioni_target = ['anger', 'disgust', 'fear', 'happiness', 'sadness', 'surprise', 'neutral']
    emotion_history = {em: [] for em in emozioni_target}
    frame_indices = []

    frame_count = 0
    skip_frames = 5
    
    temp_img_path = "temp_demo_frame.jpg"

    cv2.namedWindow("Affective Computing Demo - Live Inference", cv2.WINDOW_NORMAL)

    # Inizializziamo la nostra singola barra di caricamento
    pbar = tqdm(total=total_frames, desc="Elaborazione Video", unit="frame", dynamic_ncols=True)

    # Salviamo un riferimento all'output standard degli errori
    original_stderr = sys.stderr

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        if frame_count % skip_frames == 0:
            
            cv2.imwrite(temp_img_path, frame)
            
            # --- INIZIO SILENZIAMENTO PY-FEAT ---
            # Deviamo stderr verso il nulla per nascondere la barra di Py-Feat
            sys.stderr = open(os.devnull, 'w') 
            try:
                prediction = detector.detect_image(temp_img_path)
            finally:
                # Ripristiniamo immediatamente l'output
                sys.stderr.close()
                sys.stderr = original_stderr
            # --- FINE SILENZIAMENTO ---
            
            if not prediction.empty and len(prediction) > 0:
                face_pred = prediction.iloc[0]
                
                score_col = 'FaceScore' if 'FaceScore' in face_pred else 'face_score' if 'face_score' in face_pred else None
                face_score = float(face_pred[score_col]) if score_col else 1.0
                
                if face_score > 0.8:
                    emotions_val = face_pred[emozioni_target]
                    for em in emozioni_target:
                        emotion_history[em].append(float(emotions_val[em]))
                    frame_indices.append(frame_count)
                    
                    dom_emo = emotions_val.astype(float).idxmax()
                    
                    try:
                        x = int(face_pred.get('FaceRectX', 0))
                        y = int(face_pred.get('FaceRectY', 0))
                        w = int(face_pred.get('FaceRectWidth', 150))
                        h = int(face_pred.get('FaceRectHeight', 150))
                        
                        if w > 0 and h > 0:
                            cv2.rectangle(frame, (x, y), (x+w, y+h), (56, 189, 248), 2)
                            cv2.putText(frame, f"{dom_emo.upper()} ({face_score:.2f})", (x, y-10), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (56, 189, 248), 2)
                    except:
                        cv2.putText(frame, f"Emozione: {dom_emo.upper()}", (30, 50), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (56, 189, 248), 2)
                
            cv2.imshow("Affective Computing Demo - Live Inference", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\nInterruzione manuale richiesta.")
                break

        # Aggiorniamo la nostra barra di caricamento principale
        pbar.update(1)
        frame_count += 1

    # Chiudiamo la barra di caricamento e le finestre
    pbar.close()
    cap.release()
    cv2.destroyAllWindows()
    
    if os.path.exists(temp_img_path):
        os.remove(temp_img_path)
        
    print("🎬 Analisi video completata. Generazione del grafico in corso...")

    if len(frame_indices) > 0:
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(12, 6))
        
        color_map = {
            'anger': '#ef4444', 'disgust': '#10b981', 'fear': '#8b5cf6', 
            'happiness': '#eab308', 'sadness': '#3b82f6', 'surprise': '#f97316', 'neutral': '#94a3b8'
        }
        
        for em, values in emotion_history.items():
            ax.plot(frame_indices, values, label=em.capitalize(), color=color_map[em], linewidth=2)

        ax.set_title("Dinamica delle Emozioni (Time-Series)", fontsize=16, color="#f8fafc", pad=20)
        ax.set_xlabel("Frame Analizzati", fontsize=12)
        ax.set_ylabel("Intensità (0.0 - 1.0)", fontsize=12)
        ax.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
        ax.grid(True, linestyle='--', alpha=0.3)
        plt.tight_layout()
        plt.show()
    else:
        print("Nessun dato emotivo estratto (FaceScore sempre < 0.8 o nessun volto).")

if __name__ == "__main__":
    VIDEO_DEMO_PATH = "C:/Users/dodod/WPy64-31180/VIDEO/WolfgangLanger_Pexels.mp4" 
    
    if os.path.exists(VIDEO_DEMO_PATH):
        esegui_demo_live(VIDEO_DEMO_PATH)
    else:
        print(f"⚠️ Inserisci un percorso valido per il video demo. File non trovato: {VIDEO_DEMO_PATH}")