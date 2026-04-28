import requests
import json

def search_vinted(suchbegriff: str, anzahl: int = 50) -> list:
    
    session = requests.Session()
    
    session.get("https://www.vinted.de", headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    })
    
    cookies = session.cookies.get_dict()
    
    url = "https://www.vinted.de/api/v2/catalog/items"
    
    params = {
        "search_text": suchbegriff,
        "per_page": anzahl,
        "order": "relevance"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json",
        "X-Csrf-Token": cookies.get("CSRF-TOKEN", "")
    }
    
    response = session.get(url, params=params, headers=headers)
    
    if response.status_code != 200:
        print(f"Fehler: Status {response.status_code}")
        return []
    
    daten = response.json()
    artikel_liste = []
    
    for item in daten.get("items", []):
        artikel = {
            "titel":        item.get("title", ""),
            "preis":        float(item.get("price", {}).get("amount", 0)),
            "marke":        item.get("brand_title", ""),
            "groesse":      item.get("size_title", ""),
            "zustand":      item.get("status", ""),
            "favoriten":    item.get("favourite_count", 0),
            "url":          f"https://www.vinted.de{item.get('path', '')}"
        }
        artikel_liste.append(artikel)
    
    return artikel_liste


if __name__ == "__main__":
    ergebnisse = search_vinted("Nike Air Force 42")
    
    for artikel in ergebnisse:
        print(f"{artikel['titel']} | {artikel['preis']}€ | {artikel['marke']} | Favs: {artikel['favoriten']}")
    
    print(f"\nGesamt: {len(ergebnisse)} Artikel gefunden")