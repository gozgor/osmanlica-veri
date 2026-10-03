#!/usr/bin/env python3
"""
Osmanlıca kelime verisini hazırlar.

Kaynaklar:
  1. kaynak/elle-kelimeler.json  -> grubun elle hazırladığı, Türkçe anlamlı kelimeler (önceliklidir)
  2. kaikki.org Osmanlı Türkçesi verisi (Vikisözlük'ten çıkarılmış, CC BY-SA)
  3. kaynak/paragraflar.json     -> elle hazırlanan paragraflar

Çıktı (veri/ klasörü):
  seviye1.json, seviye2.json, seviye3.json, paragraflar.json, bilgi.json

Kullanım:
  python scripts/hazirla.py                 # kaikki verisini indirir
  python scripts/hazirla.py --girdi dosya.jsonl   # önceden indirilmiş dosyayı kullanır
  python scripts/hazirla.py --sadece-elle   # yalnızca elle hazırlanan listeden üretir
"""
import argparse
import datetime
import json
import os
import re
import sys
import unicodedata
import urllib.request

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KAYNAK = os.path.join(KOK, "kaynak")
CIKTI = os.path.join(KOK, "veri")
KAIKKI_URL = os.environ.get(
    "KAIKKI_URL",
    "https://kaikki.org/dictionary/Ottoman%20Turkish/kaikki.org-dictionary-OttomanTurkish.jsonl",
)

SEVIYE_ADLARI = {
    1: "1 · Kısa kelimeler",
    2: "2 · Kelimeler",
    3: "3 · Terkipler ve zor kelimeler",
}

# Alınmayacak sözcük türleri
ATLA_POS = {
    "name", "suffix", "prefix", "infix", "interfix", "affix", "circumfix",
    "character", "letter", "symbol", "punct", "abbrev", "romanization",
    "combining_form", "root", "contraction",
}
# Anlamsız/yönlendirme anlamları
ATLA_ETIKET = {"form-of", "alt-of", "abbreviation", "misspelling", "obsolete-spelling"}

ARAP_HARF = re.compile(r"^[؀-ۿ‌‍ ]+$")
HAREKE = re.compile(r"[ً-ٰٟۖ-ۭـ]")

# Akademik çevriyazıyı okul usulü çevriyazıya çevirme
ESLEME = {
    "ā": "â", "Ā": "Â", "ī": "î", "Ī": "Î", "ū": "û", "Ū": "Û",
    "ḳ": "k", "Ḳ": "K", "ṭ": "t", "Ṭ": "T", "ṣ": "s", "Ṣ": "S",
    "ḥ": "h", "Ḥ": "H", "ḫ": "h", "Ḫ": "H", "ẖ": "h",
    "ẕ": "z", "Ẕ": "Z", "ẓ": "z", "Ẓ": "Z", "ż": "z", "Ż": "Z",
    "ḍ": "d", "Ḍ": "D", "ḏ": "z", "ṯ": "s", "s̱": "s", "S̱": "S",
    "ġ": "ğ", "Ġ": "Ğ", "ñ": "n", "Ñ": "N", "ŋ": "n",
    "č": "ç", "Č": "Ç", "š": "ş", "Š": "Ş", "ž": "j", "Ž": "J",
    "ʿ": "'", "ʾ": "'", "‘": "'", "’": "'", "`": "'",
    "ẹ": "e", "ọ": "o", "ė": "e",
}
KORUNAN_ISARET = {"̂", "̧", "̆", "̈", "̇"}  # ^ ¸ ˘ ¨ ˙
GECERLI_OKUNUS = re.compile(r"^[a-zA-ZçğıöşüâîûÇĞİÖŞÜÂÎÛ' \-]+$")


def okunusu_duzelt(s):
    s = unicodedata.normalize("NFC", (s or "").strip())
    for k in sorted(ESLEME, key=len, reverse=True):
        s = s.replace(k, ESLEME[k])
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if not unicodedata.combining(c) or c in KORUNAN_ISARET)
    s = unicodedata.normalize("NFC", s)
    s = re.sub(r"\s+", " ", s).strip(" ,;")
    return s if s and GECERLI_OKUNUS.match(s) else None


def harf_sayisi(o):
    return len(re.sub(r"[\s‌‍]", "", HAREKE.sub("", o)))


def seviye_bul(o, l):
    kelime = len(l.split())
    if kelime == 1 and "-" not in l:
        n = harf_sayisi(o)
        if n <= 3:
            return 1
        if n <= 6:
            return 2
    return 3


def kaikki_oku(satirlar):
    sozluk = {}
    for satir in satirlar:
        satir = satir.strip()
        if not satir:
            continue
        try:
            g = json.loads(satir)
        except ValueError:
            continue
        if g.get("lang_code") != "ota" or g.get("pos") in ATLA_POS:
            continue
        o = unicodedata.normalize("NFC", (g.get("word") or "").strip())
        if not o or not ARAP_HARF.match(o):
            continue

        okunuslar = []
        for f in g.get("forms") or []:
            if "romanization" in (f.get("tags") or []):
                okunuslar.append(f.get("form"))
        for h in g.get("head_templates") or []:
            tr = (h.get("args") or {}).get("tr")
            if tr:
                okunuslar.extend(tr.split(","))
        okunuslar = [x for x in (okunusu_duzelt(r) for r in okunuslar) if x]
        if not okunuslar:
            continue

        anlamlar = []
        for s in g.get("senses") or []:
            if s.get("form_of") or s.get("alt_of"):
                continue
            if ATLA_ETIKET & set(s.get("tags") or []):
                continue
            gl = (s.get("glosses") or [None])[0]
            if gl:
                gl = re.sub(r"\s+", " ", gl).strip()
                if len(gl) > 90:
                    gl = gl[:87].rstrip() + "…"
                anlamlar.append(gl)
        if not anlamlar:
            continue

        bugun = None
        for d in g.get("descendants") or []:
            if d.get("lang_code") == "tr" and d.get("word"):
                bugun = d["word"].strip()
                break

        k = sozluk.setdefault(o, {"o": o, "okunuslar": [], "e": [], "t": None})
        for r in okunuslar:
            if r not in k["okunuslar"]:
                k["okunuslar"].append(r)
        for a in anlamlar:
            if a not in k["e"]:
                k["e"].append(a)
        k["t"] = k["t"] or bugun
    return sozluk


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--girdi", help="Önceden indirilmiş kaikki JSONL dosyası")
    ap.add_argument("--sadece-elle", action="store_true")
    ap.add_argument("--en-az", type=int, default=500,
                    help="kaikki'den bundan az kelime gelirse hata ver (bozuk indirmeye karşı)")
    args = ap.parse_args()

    with open(os.path.join(KAYNAK, "elle-kelimeler.json"), encoding="utf-8") as f:
        elle = json.load(f)
    with open(os.path.join(KAYNAK, "paragraflar.json"), encoding="utf-8") as f:
        paragraflar = json.load(f)

    seviyeler = {1: [], 2: [], 3: []}
    gorulen = set()
    for k in elle:
        it = {"o": k["o"], "l": k["l"], "a": k["a"]}
        if k.get("v"):
            it["v"] = k["v"]
        seviyeler[int(k.get("seviye") or seviye_bul(k["o"], k["l"]))].append(it)
        gorulen.add(unicodedata.normalize("NFC", k["o"]))

    vikiden = 0
    if not args.sadece_elle:
        if args.girdi:
            with open(args.girdi, encoding="utf-8") as f:
                sozluk = kaikki_oku(f)
        else:
            print("İndiriliyor:", KAIKKI_URL, file=sys.stderr)
            req = urllib.request.Request(KAIKKI_URL, headers={"User-Agent": "osmanlica-veri (github.com/gozgor)"})
            with urllib.request.urlopen(req, timeout=300) as r:
                sozluk = kaikki_oku(r.read().decode("utf-8").splitlines())
        if len(sozluk) < args.en_az:
            sys.exit("kaikki'den yalnızca %d kelime geldi, dosyalar güncellenmedi." % len(sozluk))
        for o in sorted(sozluk):
            if o in gorulen:
                continue
            k = sozluk[o]
            it = {"o": o, "l": k["okunuslar"][0], "e": "; ".join(k["e"][:3])}
            if len(k["okunuslar"]) > 1:
                it["v"] = k["okunuslar"][1:4]
            if k["t"]:
                it["t"] = k["t"]
            seviyeler[seviye_bul(o, it["l"])].append(it)
            vikiden += 1

    os.makedirs(CIKTI, exist_ok=True)

    def yaz(ad, veri):
        with open(os.path.join(CIKTI, ad), "w", encoding="utf-8") as f:
            json.dump(veri, f, ensure_ascii=False, separators=(",", ":"))

    for n, items in seviyeler.items():
        yaz("seviye%d.json" % n, {"ad": SEVIYE_ADLARI[n], "items": items})
    yaz("paragraflar.json", {"ad": "4 · Paragraf", "para": True, "items": paragraflar})
    bilgi = {
        "guncelleme": datetime.date.today().isoformat(),
        "elle": len(elle),
        "vikisozluk": vikiden,
        "seviyeler": {str(n): len(v) for n, v in seviyeler.items()},
        "paragraf": len(paragraflar),
        "kaynak": "Vikisözlük (en.wiktionary.org) verisi, kaikki.org aracılığıyla. Lisans: CC BY-SA 4.0",
    }
    yaz("bilgi.json", bilgi)
    print(json.dumps(bilgi, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
