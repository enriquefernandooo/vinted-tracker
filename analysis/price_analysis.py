import statistics
from scrapers.vinted_scraper import search_vinted

def analyse_preise(suchbegriff: str, einkaufspreis: float) -> dict:
    
    print(f"Suche nach: {suchbegriff}...")
    artikel = search_vinted(suchbegriff)
    
    if not artikel:
        print("Keine Artikel gefunden.")
        return {}
    
    preise = [a["preis"] for a in artikel if a["preis"] > 0]
    
    if not preise:
        print("Keine Preise gefunden.")
        return {}
    
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
    ergebnis = analyse_preise("Nike Air Force 42", einkaufspreis=20.0)
    print_analyse(ergebnis)