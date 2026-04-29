import os
from dotenv import load_dotenv
from supabase import create_client
from analysis.price_analysis import analyse_preise

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def update_alle_artikel():
    # Alle aktiven Artikel holen
    result = supabase.table("inventory").select("*").eq("status", "aktiv").execute()
    artikel_liste = result.data

    if not artikel_liste:
        print("Keine aktiven Artikel gefunden.")
        return

    print(f"{len(artikel_liste)} aktive Artikel gefunden.")

    for artikel in artikel_liste:
        print(f"Analysiere: {artikel['artikel']}...")

        try:
            ergebnis = analyse_preise(artikel['artikel'], artikel['einkaufspreis'])

            if not ergebnis:
                print(f"Keine Ergebnisse für {artikel['artikel']}")
                continue

            # Historie speichern
            supabase.table("preis_historie").insert({
                "artikel_id":      artikel['id'],
                "empfohlener_vk":  ergebnis['empfehlung'],
                "median_preis":    ergebnis['median'],
                "anzahl_listings": ergebnis['anzahl_artikel'],
            }).execute()

            # Ziel VK in inventory aktualisieren
            supabase.table("inventory").update({
                "ziel_verkaufspreis": ergebnis['empfehlung']
            }).eq("id", artikel['id']).execute()

            print(f"✓ {artikel['artikel']} → {ergebnis['empfehlung']}€")

        except Exception as e:
            print(f"Fehler bei {artikel['artikel']}: {e}")

    print("Update abgeschlossen.")

if __name__ == "__main__":
    update_alle_artikel()