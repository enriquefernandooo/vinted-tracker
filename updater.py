import os
import sys
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime, timedelta
from analysis.price_analysis import analyse_preise

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def sammle_preise():
    """Läuft stündlich – sammelt Preise und speichert in Historie"""
    result = supabase.table("inventory").select("*").eq("status", "aktiv").execute()
    artikel_liste = result.data

    if not artikel_liste:
        print("Keine aktiven Artikel gefunden.")
        return

    print(f"{len(artikel_liste)} aktive Artikel gefunden.")

    for artikel in artikel_liste:
        print(f"Sammle Preise für: {artikel['artikel']}...")

        try:
            ergebnis = analyse_preise(artikel['artikel'], artikel['einkaufspreis'])

            if not ergebnis:
                continue

            supabase.table("preis_historie").insert({
                "artikel_id":      artikel['id'],
                "empfohlener_vk":  ergebnis['empfehlung'],
                "median_preis":    ergebnis['median'],
                "anzahl_listings": ergebnis['anzahl_artikel'],
            }).execute()

            print(f"✓ {artikel['artikel']} → {ergebnis['empfehlung']}€ gespeichert")

        except Exception as e:
            print(f"Fehler bei {artikel['artikel']}: {e}")

    print("Sammlung abgeschlossen.")


def berechne_tages_vk():
    """Läuft täglich um 9 Uhr – berechnet Durchschnitt der letzten 24h"""
    result = supabase.table("inventory").select("*").eq("status", "aktiv").execute()
    artikel_liste = result.data

    if not artikel_liste:
        print("Keine aktiven Artikel gefunden.")
        return

    from datetime import timezone
    vor_24h = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()

    for artikel in artikel_liste:
        print(f"Berechne Tages-VK für: {artikel['artikel']}...")

        try:
            historie = supabase.table("preis_historie")\
                .select("empfohlener_vk")\
                .eq("artikel_id", artikel['id'])\
                .gte("datum", vor_24h)\
                .execute()

            eintraege = historie.data

            if not eintraege:
                print(f"Keine Daten der letzten 24h für {artikel['artikel']}")
                continue

            durchschnitt = sum(e['empfohlener_vk'] for e in eintraege) / len(eintraege)
            durchschnitt = round(durchschnitt, 2)

            supabase.table("inventory").update({
                "ziel_verkaufspreis": durchschnitt
            }).eq("id", artikel['id']).execute()

            print(f"✓ {artikel['artikel']} → Tages-VK: {durchschnitt}€ (aus {len(eintraege)} Messungen)")

        except Exception as e:
            print(f"Fehler bei {artikel['artikel']}: {e}")

    print("Tages-VK Update abgeschlossen.")


if __name__ == "__main__":
    modus = sys.argv[1] if len(sys.argv) > 1 else "sammeln"

    if modus == "sammeln":
        sammle_preise()
    elif modus == "tagesvk":
        berechne_tages_vk()