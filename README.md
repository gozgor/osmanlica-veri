# Osmanlıca Veri

Osmanlıca okuma alıştırması için kelime ve paragraf verisi. Dosyalar jsDelivr CDN'i üzerinden herkese açık olarak sunulur ve Blogger'daki alıştırma sayfası bu adreslerden okur.

## Adresler

| Dosya | Adres |
|---|---|
| Seviye 1 (kısa kelimeler) | https://cdn.jsdelivr.net/gh/gozgor/osmanlica-veri@main/veri/seviye1.json |
| Seviye 2 (kelimeler) | https://cdn.jsdelivr.net/gh/gozgor/osmanlica-veri@main/veri/seviye2.json |
| Seviye 3 (terkipler, zor kelimeler) | https://cdn.jsdelivr.net/gh/gozgor/osmanlica-veri@main/veri/seviye3.json |
| Paragraflar | https://cdn.jsdelivr.net/gh/gozgor/osmanlica-veri@main/veri/paragraflar.json |
| Özet bilgi | https://cdn.jsdelivr.net/gh/gozgor/osmanlica-veri@main/veri/bilgi.json |

## Klasörler

- `kaynak/elle-kelimeler.json`: Grubun elle hazırladığı kelimeler. Türkçe anlamları vardır ve Vikisözlük verisinden önceliklidir.
- `kaynak/paragraflar.json`: Paragraflar (Osmanlıca metin, Latin okunuş, anlam).
- `scripts/hazirla.py`: Vikisözlük verisini indirip `veri/` klasörünü üreten betik.
- `veri/`: Üretilen dosyalar. **Elle düzenlemeyin**, her çalıştırmada yeniden yazılır.

## Kelime veya paragraf eklemek

1. GitHub'da `kaynak/elle-kelimeler.json` ya da `kaynak/paragraflar.json` dosyasını açın, kalem simgesine basın.
2. Aynı biçimde yeni satır ekleyin:
   - Kelime: `{ "o": "قلم", "l": "kalem", "a": "kalem", "seviye": 1 }`
     (`v` ile kabul edilecek diğer okunuşlar eklenebilir: `"v": ["kitap"]`)
   - Paragraf: `{ "o": "Osmanlıca metin", "l": "Latin okunuş", "a": "Bugünkü Türkçe anlamı" }`
3. "Commit changes" deyin. Otomatik görev birkaç dakika içinde `veri/` klasörünü günceller. CDN'e yansıması birkaç saat sürebilir.

Virgül unutulursa dosya bozulur ve görev hata verir; Actions sekmesinde kırmızı çarpı görürseniz son değişikliği kontrol edin.

## Otomatik güncelleme

`.github/workflows/guncelle.yml` görevi her ayın 1'inde Vikisözlük verisini yeniden indirir. Actions sekmesinden **Kelimeleri güncelle → Run workflow** ile istediğiniz zaman da çalıştırabilirsiniz.

Vikisözlük kelimelerinde anlamlar İngilizcedir (`e` alanı); varsa bugünkü Türkçe karşılığı `t` alanında verilir.

## Kaynak ve lisans

Kelimelerin büyük kısmı [Vikisözlük](https://en.wiktionary.org/wiki/Category:Ottoman_Turkish_lemmas) maddelerinden, [kaikki.org](https://kaikki.org/dictionary/Ottoman%20Turkish/index.html) üzerinden alınmıştır. Vikisözlük içeriği [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.tr) lisanslıdır; bu depodaki veri de aynı lisansla paylaşılır. Kullanırken kaynak gösterin.
