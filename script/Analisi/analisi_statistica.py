import os
import pandas as pd
import numpy as np
from scipy.stats import shapiro, ttest_ind, mannwhitneyu

def calculate_cohens_d(group1, group2):
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    if (n1 + n2 - 2) == 0:
        return 0
    pooled_se = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    return (np.mean(group1) - np.mean(group2)) / pooled_se if pooled_se != 0 else 0

def benjamini_hochberg_fdr(p_values):
    """
    Applica la correzione FDR di Benjamini-Hochberg ai p-value in modo nativo.
    (Senza usare moduli esterni pesanti come statsmodels)
    """
    n = len(p_values)
    if n == 0:
        return []
    
    sorted_indices = np.argsort(p_values)
    sorted_p_values = np.array(p_values)[sorted_indices]
    
    adjusted_p = np.zeros(n)
    min_adj_p = 1.0
    for i in range(n - 1, -1, -1):
        j = i + 1
        adj_p = sorted_p_values[i] * n / j
        min_adj_p = min(min_adj_p, adj_p)
        adjusted_p[sorted_indices[i]] = min(1.0, min_adj_p)
        
    return adjusted_p.tolist()

def esegui_analisi_statistica(file_dataset1, file_dataset2, cartella_output, filtro_metriche='all', nome_base='Risultati'):
    print("=" * 60)
    print(" AVVIO ANALISI STATISTICA COMPARATIVA")
    print("=" * 60)
    print(f"File Dataset 1: {os.path.basename(file_dataset1)}")
    print(f"File Dataset 2: {os.path.basename(file_dataset2)}")
    print(f"Nome Output Base: {nome_base}")
    print("-" * 60)
    
    try:
        if file_dataset1.endswith('.xlsx'):
            df_ds1 = pd.read_excel(file_dataset1)
            df_ds2 = pd.read_excel(file_dataset2)
        else:
            df_ds1 = pd.read_json(file_dataset1)
            df_ds2 = pd.read_json(file_dataset2)
            
        print(f"Dati caricati: Dataset 1 (n={len(df_ds1)}), Dataset 2 (n={len(df_ds2)})")
        
        # Identifica le colonne numeriche valide comuni tra i due file
        cols_ds1 = set(df_ds1.select_dtypes(include=[np.number]).columns)
        cols_ds2 = set(df_ds2.select_dtypes(include=[np.number]).columns)
        feature_cols = list(cols_ds1.intersection(cols_ds2))
        
        # Filtro Metriche (Opzione B)
        if filtro_metriche == 'mean':
            feature_cols = [c for c in feature_cols if c.startswith('Mean_')]
            print("      > Filtro attivo: Analisi limitata SOLO alle Medie (Mean_).")
        elif filtro_metriche == 'std':
            feature_cols = [c for c in feature_cols if c.startswith('Std_')]
            print("      > Filtro attivo: Analisi limitata SOLO alle Varianze (Std_).")
        elif filtro_metriche == 'max':
            feature_cols = [c for c in feature_cols if c.startswith('Max_')]
            print("      > Filtro attivo: Analisi limitata SOLO ai Picchi (Max_).")
            
        if not feature_cols:
            print("      > ERRORE: Nessuna colonna numerica in comune trovata nei due file.")
            return False
            
        print(f"Trovate {len(feature_cols)} metriche cliniche da confrontare.")
        
        risultati = []
        p_values = []
        
        for col in feature_cols:
            data_ds1 = df_ds1[col].dropna()
            data_ds2 = df_ds2[col].dropna()
            
            if len(data_ds1) < 3 or len(data_ds2) < 3:
                continue
                
            mean_ds1 = data_ds1.mean()
            mean_ds2 = data_ds2.mean()
            
            # 1. Test Normalità (Shapiro-Wilk)
            try:
                _, p_shapiro_ds1 = shapiro(data_ds1)
                _, p_shapiro_ds2 = shapiro(data_ds2)
                is_normal = (p_shapiro_ds1 >= 0.05) and (p_shapiro_ds2 >= 0.05)
            except Exception:
                is_normal = False
                
            # 2. Test Significatività e Effect Size
            try:
                if is_normal:
                    # Metodo Parametrico
                    stat_val, p_val = ttest_ind(data_ds1, data_ds2, equal_var=False)
                    test_usato = "T-Test (Welch)"
                    effect_size = calculate_cohens_d(data_ds1, data_ds2)
                    effetto_tipo = "Cohen's d"
                else:
                    # Metodo Non Parametrico
                    stat_val, p_val = mannwhitneyu(data_ds1, data_ds2, alternative='two-sided')
                    test_usato = "Mann-Whitney U"
                    # Effect Size r
                    n1, n2 = len(data_ds1), len(data_ds2)
                    effect_size = 1 - (2 * stat_val) / (n1 * n2)
                    effetto_tipo = "Rank-Biserial (r)"
            except Exception as e:
                print(f"      > Errore analisi colonna {col}: {e}")
                continue
                
            risultati.append({
                'Metrica': col,
                'Media Dataset 1': mean_ds1,
                'Media Dataset 2': mean_ds2,
                'Distribuzione': 'Normale' if is_normal else 'Non Normale',
                'Test Usato': test_usato,
                'P-Value Raw': p_val,
                'Significativo (Grezzo)?': 'SI' if p_val < 0.05 else 'NO',
                'Effect Size': abs(effect_size),
                'Tipo Effect Size': effetto_tipo,
                'Chi è più alto?': 'Dataset 1' if mean_ds1 > mean_ds2 else 'Dataset 2' if mean_ds2 > mean_ds1 else 'Uguale'
            })
            p_values.append(p_val)
            
        if not risultati:
            print("      > Nessuna metrica valida elaborata.")
            return False
            
        # 3. Correzione Falsi Positivi (FDR)
        p_adj = benjamini_hochberg_fdr(p_values)
        
        for i, res in enumerate(risultati):
            res['P-Value Adjusted (FDR)'] = p_adj[i]
            res['Significativo (FDR)?'] = 'SI' if p_adj[i] < 0.05 else 'NO'
            
        # 4. Esportazione Dati
        df_risultati = pd.DataFrame(risultati)
        # Ordino prima per significatività grezza e poi per P-value, così i risultati promettenti sono in cima
        df_risultati = df_risultati.sort_values(by=['Significativo (Grezzo)?', 'P-Value Raw'], ascending=[False, True])
        
        cols_order = ['Metrica', 'Significativo (FDR)?', 'Significativo (Grezzo)?', 'P-Value Adjusted (FDR)', 'P-Value Raw', 
                      'Test Usato', 'Effect Size', 'Tipo Effect Size', 'Chi è più alto?', 
                      'Media Dataset 1', 'Media Dataset 2', 'Distribuzione']
        df_risultati = df_risultati[cols_order]
        
        out_excel = os.path.join(cartella_output, f"{nome_base}_{filtro_metriche}.xlsx")
        out_json = os.path.join(cartella_output, f"{nome_base}_{filtro_metriche}.json")
        
        df_risultati.to_excel(out_excel, index=False)
        df_risultati.to_json(out_json, orient="records", indent=4)
        
        print(f"\n      > Analisi Statistica completata con successo!")
        print(f"      > Metriche totali analizzate: {len(risultati)}")
        sig_fdr = len(df_risultati[df_risultati['Significativo (FDR)?'] == 'SI'])
        sig_raw = len(df_risultati[df_risultati['Significativo (Grezzo)?'] == 'SI'])
        print(f"      > Metriche significative con correzione FDR: {sig_fdr}")
        print(f"      > Metriche significative (P-Value Grezzo esplorativo): {sig_raw}")
        print("\n" + "=" * 60)
        print(" ELABORAZIONE TERMINATA CON SUCCESSO")
        print("=" * 60)
        print(f"File Excel salvato in: {out_excel}")
        print(f"File JSON salvato in: {out_json}\n")
        
        return True
        
    except Exception as e:
        print(f"\n      > ERRORE CRITICO durante l'analisi statistica: {e}")
        return False
