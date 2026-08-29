# Nutella Hediye Takip Botu

Nutella "Mutluluğa Puan" hediyeler sayfasını (https://www.nutella.com/tr/tr/xp/mutlulugapuan/hediyeler/)
her 5 dakikada bir kontrol eder, "Tükendi" durumundan "Stokta"ya geçen ya da yeni eklenen
hediyeleri Telegram'dan anında haber verir.

## Kurulum (5 dakika, tamamen ücretsiz)

### 1. GitHub'da yeni bir repo oluşturun
- github.com üzerinden "New repository" ile boş bir repo açın (isim önemli değil, örn. `nutella-watcher`).
- Public ya da Private fark etmez.

### 2. Bu dosyaları repoya yükleyin
Bu klasördeki tüm dosyaları (watch.py, .github/workflows/watch.yml, README.md) repoya
yükleyin. En kolay yol: GitHub web arayüzünde "Add file > Upload files" ile sürükle-bırak.

### 3. Telegram bilgilerinizi "Secret" olarak ekleyin
Repo sayfasında: **Settings > Secrets and variables > Actions > New repository secret**

İki secret ekleyin:
- `TELEGRAM_BOT_TOKEN` → botunuzun token'ı
- `TELEGRAM_CHAT_ID` → `6130452131`

(Token'ı buraya, koda YAZMAYIN — sadece Secrets kısmına eklemeniz yeterli, workflow dosyası
zaten oradan otomatik okuyor.)

### 4. Actions'ı etkinleştirin
Repo sayfasında **Actions** sekmesine girin, eğer "workflow'ları etkinleştir" gibi bir
onay isteniyorsa onaylayın.

### 5. İlk çalıştırmayı elle tetikleyin (test için)
Actions sekmesi > "Nutella Hediye Takip" workflow'u > sağ üstten **Run workflow** butonuna
basın. Birkaç dakika içinde tamamlanmalı. Yeşil tik görürseniz her şey doğru kurulmuş demektir.

Bundan sonra otomatik olarak her 5 dakikada bir kendi kendine çalışacak ve durum değişikliği
olduğunda Telegram'a mesaj atacaktır.

## Nasıl çalışır?
- `watch.py`, siteyi headless tarayıcı (Playwright) ile açar, tüm hediye kartlarını okur.
- Her hediyenin adını ve "tükendi mi" bilgisini `state.json` dosyasına kaydeder.
- Bir sonraki çalıştırmada önceki durumla karşılaştırır:
  - Tükendi → Stokta geçişi: 🎉 bildirimi
  - Daha önce olmayan yeni bir hediye: 🆕 bildirimi
- `state.json` her çalıştırma sonunda otomatik olarak repoya commit'lenir, böylece bir
  sonraki çalıştırma neyin değiştiğini bilir.

## Notlar / olası sorunlar
- Nutella sitesinin HTML yapısı (class isimleri) değişirse script hediyeleri bulamayabilir;
  bu durumda Actions loglarında "Hiç hediye bulunamadı" uyarısı görürsünüz — bana class
  isimlerini tekrar gönderirseniz güncellerim.
- GitHub Actions'ın ücretsiz planında ayda 2000 dakika limiti var; 5 dakikada bir ~1-2 dk
  süren bir çalıştırma bu limitin oldukça altında kalır.
- Cron zamanlaması GitHub tarafında yoğunlukta birkaç dakika gecikebilir, bu normaldir.
