import math

def calculate_ear(eye_points):
    """
    Calcola l'Eye Aspect Ratio (EAR) per stimare l'apertura dell'occhio.
    :param eye_points: Lista di 6 tuple (x, y) che rappresentano i landmarks dell'occhio.
    :return: Valore float dell'EAR.
    """
    try:
        # A: distanza verticale tra i punti 1 e 5
        A = math.dist(eye_points[1], eye_points[5])
        # B: distanza verticale tra i punti 2 e 4
        B = math.dist(eye_points[2], eye_points[4])
        # C: distanza orizzontale tra i punti 0 e 3
        C = math.dist(eye_points[0], eye_points[3])
        
        if C == 0:
            return 0.0
        
        ear = (A + B) / (2.0 * C)
        return ear
    except Exception:
        return 0.0

def calculate_mar(mouth_points):
    """
    Calcola il Mouth Aspect Ratio (MAR) per stimare l'apertura della bocca.
    :param mouth_points: Lista di 12 tuple (x, y) che rappresentano i landmarks del bordo esterno labbra (48-59).
    :return: Valore float del MAR.
    """
    try:
        # A, B, C: distanze verticali
        A = math.dist(mouth_points[2], mouth_points[10]) # Punti 50, 58
        B = math.dist(mouth_points[3], mouth_points[9])  # Punti 51, 57
        C = math.dist(mouth_points[4], mouth_points[8])  # Punti 52, 56
        # D: distanza orizzontale
        D = math.dist(mouth_points[0], mouth_points[6])  # Punti 48, 54
        
        if D == 0:
            return 0.0
        
        mar = (A + B + C) / (3.0 * D)
        return mar
    except Exception:
        return 0.0

