import statistics
from scrapers.vinted_scraper import search_vinted

def analyse_preise(suchbegriff: str, einkaufspreis: float) -> dict:
    
    print(f"Suche nach: {suchbegriff}...")
    artikel = search_vinted(suchbegriff)
    
    if not artikel:
        print("Keine Artikel gefunden.")
        return {}
    
    preise_alle = [a["preis"] for a in artikel if a["preis"] > 0]
    
    if not preise_alle:
        return {}
    
    # Erst Median aus allen Preisen berechnen
    median_roh = statistics.median(preise_alle)
    
    # Filter 1: Favoriten >= 3
    # Filter 2: Preis innerhalb ±40% vom Median
    gefiltert = [
        a for a in artikel
        if a["preis"] > 0
        and a["favoriten"] >= 5
        and median_roh * 0.6 <= a["preis"] <= median_roh * 1.4
    ]
    
    print(f"Vor Filter: {len(artikel)} Artikel")
    print(f"Nach Filter: {len(gefiltert)} Artikel")
    
    if len(gefiltert) < 5:
        print("Zu wenige Artikel nach Filter – nehme ungefilterte Daten")
        gefiltert = [a for a in artikel if a["preis"] > 0]
    
    preise = [a["preis"] for a in gefiltert]
    
    median        = statistics.median(preise)
    durchschnitt  = statistics.mean(preise)
    minimum       = min(preise)
    maximum       = max(preise)
    empfehlung    = round(median * 0.95, 2)
    marge         = round(empfehlung - einkaufspreis, 2)
    marge_prozent = round((marge / einkaufspreis) * 100, 1)
    
    ergebnis = {
        "suchbegriff":    suchbegriff,
        "anzahl_artikel": len(preise),
        "median":         median,
        "durchschnitt":   round(durchschnitt, 2),
        "minimum":        minimum,
        "maximum":        maximum,
        "empfehlung":     empfehlung,
        "einkaufspreis":  einkaufspreis,
        "marge_euro":     marge,
        "marge_prozent":  marge_prozent
    }
    
    return ergebnis


def print_analyse(ergebnis: dict):
    print("\n" + "="*45)
    print(f"  Analyse: {ergebnis['suchbegriff']}")
    print("="*45)
    print(f"  Artikel analysiert:   {ergebnis['anzahl_artikel']}")
    print(f"  Median Preis:         {ergebnis['median']}€")
    print(f"  Durchschnitt:         {ergebnis['durchschnitt']}€")
    print(f"  Günstigstes:          {ergebnis['minimum']}€")
    print(f"  Teuerstes:            {ergebnis['maximum']}€")
    print("-"*45)
    print(f"  Empfohlener VK:       {ergebnis['empfehlung']}€")
    print(f"  Dein Einkaufspreis:   {ergebnis['einkaufspreis']}€")
    print(f"  Marge:                {ergebnis['marge_euro']}€  ({ergebnis['marge_prozent']}%)")
    print("="*45)


if __name__ == "__main__":
    ergebnis = analyse_preise("Barbour Steppjacke L gut", einkaufspreis=16.0)
    print_analyse(ergebnis)