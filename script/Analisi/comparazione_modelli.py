import pandas as pd
import numpy as np
import os

def esegui_comparazione_modelli(file_base, file_avanzato, cartella_out, nome_base_out="Meta_Analisi_Modelli"):
    print("=" * 60)
    print(" AVVIO META-ANALISI COMPARATIVA (BASE vs AVANZATO)")
    print("=" * 60)
    print(f"File Base: {os.path.basename(file_base)}")
    print(f"File Avanzato: {os.path.basename(file_avanzato)}")
    print(f"Nome Output: {nome_base_out}")
    print("-" * 60)
    
    try:
        # 1. Caricamento Dati
        if file_base.endswith('.xlsx'):
            df_base = pd.read_excel(file_base)
        else:
            df_base = pd.read_json(file_base)
            
        if file_avanzato.endswith('.xlsx'):
            df_adv = pd.read_excel(file_avanzato)
        else:
            df_adv = pd.read_json(file_avanzato)
            
        print(f"Dati caricati: Modello Base ({len(df_base)} metriche), Modello Avanzato ({len(df_adv)} metriche)")
        
        # 2. Merge dei dati usando la Metrica come chiave
        df_merged = pd.merge(df_base, df_adv, on='Metrica', suffixes=('_Base', '_Adv'), how='outer')
        
        # 3. Logica di comparazione
        risultati = []
        for index, row in df_merged.iterrows():
            metrica = row['Metrica']
            is_base = not pd.isna(row.get('P-Value Raw_Base', np.nan))
            is_adv = not pd.isna(row.get('P-Value Raw_Adv', np.nan))
            
            if is_base and is_adv:
                stato = "Comune"
                
                # Calcolo shift di Significatività Grezza
                sig_grezzo_base = str(row.get('Significativo (Grezzo)?_Base', 'NO')).strip().upper()
                sig_grezzo_adv = str(row.get('Significativo (Grezzo)?_Adv', 'NO')).strip().upper()
                
                if sig_grezzo_base == 'NO' and sig_grezzo_adv == 'SI':
                    shift_grezzo = "Migliorato (Scoperta)"
                elif sig_grezzo_base == 'SI' and sig_grezzo_adv == 'NO':
                    shift_grezzo = "Peggiorato (Persa)"
                else:
                    shift_grezzo = "Invariato"
                    
                # Calcolo shift di Significatività FDR
                sig_fdr_base = str(row.get('Significativo (FDR)?_Base', 'NO')).strip().upper()
                sig_fdr_adv = str(row.get('Significativo (FDR)?_Adv', 'NO')).strip().upper()
                
                if sig_fdr_base == 'NO' and sig_fdr_adv == 'SI':
                    shift_fdr = "Migliorato (Scoperta)"
                elif sig_fdr_base == 'SI' and sig_fdr_adv == 'NO':
                    shift_fdr = "Peggiorato (Persa)"
                else:
                    shift_fdr = "Invariato"
                    
                # Calcolo Delta Effect Size (positivo = effetto più grande nel modello avanzato)
                eff_base = float(row.get('Effect Size_Base', 0))
                eff_adv = float(row.get('Effect Size_Adv', 0))
                delta_effect = round(eff_adv - eff_base, 4)
                
            elif is_adv and not is_base:
                stato = "Esclusiva Avanzato (EAR/MAR)"
                shift_grezzo = "N/A"
                shift_fdr = "N/A"
                delta_effect = None
            else:
                stato = "Esclusiva Base"
                shift_grezzo = "N/A"
                shift_fdr = "N/A"
                delta_effect = None
                
            # Salvataggio riga
            risultati.append({
                'Metrica': metrica,
                'Stato': stato,
                'Shift Significatività (Grezzo)': shift_grezzo,
                'Shift Significatività (FDR)': shift_fdr,
                'Delta Effect Size (Adv - Base)': delta_effect,
                'P-Value Grezzo (Base)': row.get('P-Value Raw_Base', None),
                'P-Value Grezzo (Adv)': row.get('P-Value Raw_Adv', None),
                'Effect Size (Base)': row.get('Effect Size_Base', None),
                'Effect Size (Adv)': row.get('Effect Size_Adv', None)
            })
            
        # 4. Esportazione
        df_risultati = pd.DataFrame(risultati)
        # Ordino prima per scoperte in modo che saltino subito all'occhio
        df_risultati['Ordine'] = df_risultati['Shift Significatività (Grezzo)'].map({
            'Migliorato (Scoperta)': 1,
            'Invariato': 2,
            'Peggiorato (Persa)': 3,
            'N/A': 4
        })
        df_risultati = df_risultati.sort_values(by=['Ordine', 'Stato'])
        df_risultati = df_risultati.drop(columns=['Ordine'])
        
        out_excel = os.path.join(cartella_out, f"{nome_base_out}.xlsx")
        out_json = os.path.join(cartella_out, f"{nome_base_out}.json")
        
        df_risultati.to_excel(out_excel, index=False)
        df_risultati.to_json(out_json, orient="records", indent=4)
        
        # 5. Sommario su Console
        print("\n      > Report Meta-Analisi generato con successo!")
        scoperte = len(df_risultati[df_risultati['Shift Significatività (Grezzo)'] == 'Migliorato (Scoperta)'])
        esclusive = len(df_risultati[df_risultati['Stato'] == 'Esclusiva Avanzato (EAR/MAR)'])
        
        print(f"      > Metriche migliorate (da 'NO' a 'SI'): {scoperte}")
        print(f"      > Metriche esclusive analizzate: {esclusive}")
        print("\n" + "=" * 60)
        print(" ELABORAZIONE TERMINATA CON SUCCESSO")
        print("=" * 60)
        print(f"File salvati nella cartella: {cartella_out}")
        return True
        
    except Exception as e:
        print(f"\n ERRORE imprevisto durante la meta-analisi: {e}")
        return False
