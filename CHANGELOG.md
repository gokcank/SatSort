# 📋 SatSort Değişiklik Günlüğü (Changelog)

Bu projedeki tüm önemli değişiklikler bu dosyada kronolojik olarak listelenmektedir.
Format, [Keep a Changelog](https://keepachangelog.com/tr/1.0.0/) standartlarına ve [Semantic Versioning](https://semver.org/lang/tr/) kurallarına dayanmaktadır.

## [v1.0.1] - 2026-08-21

### 🐛 Hata Düzeltmeleri ve İyileştirmeler (Bug Fixes & Improvements)

* **🌐 Dil Dosyası (i18n) Paketleme Düzeltmesi:** Bağımsız binary ve `.deb` paketlerinde çeviri JSON dosyasının yüklenmesini engelleyen paketleme yolu sorunu çözüldü (`T100`, `T101` etiketleri yerine Türkçe ve seçilen dil metinleri yüklenecek şekilde düzeltildi).
* **📦 APT Deposu Desteği:** Debian, Ubuntu, Pardus ve Linux Mint için GitHub Pages tabanlı resmi APT deposu kuruldu (`deb [arch=amd64 trusted=yes] https://gokcank.github.io/SatSort stable main`).

---

## [v1.0.0] - 2026-08-21

### 🌟 İlk Resmi Sürüm (Initial Release)

Linux platformu için sıfırdan geliştirilen, modern ve tam donanımlı **SatcoDX (`.sdx`)** uydu kanal listesi düzenleyicisi **SatSort**'un ilk kararlı sürümü yayınlandı!

#### ✨ Eklenen Özellikler
* **🖱️ Sürükle & Bırak ve Araya Ekle & Kaydır (Insert & Shift):** Kanalların sırasını fareyle sürükleyerek veya `Alt+Up/Down` ile zahmetsizce düzenleme.
* **🎯 Numaraya Taşı (`Ctrl+M`):** Kanal adı ve mevcut sırasını görerek doğrudan hedef kanal numarasına taşıma.
* **🔗 Referans Liste ile Otomatik Sıralama:** Eski/favori bir `.sdx` dosyasını referans göstererek yeni taranmış yüzlerce kanalı tek tıkla eski düzene getirme.
* **🧹 Akıllı Toplu Temizlik Araçları:**
  * 📻 Radyoları listenin sonuna taşıma
  * 🔒 Şifreli kanalları tek tıkla temizleme
  * 🔤 Kanal isimlerini standartlaştırma (Büyük harf & fazlalık boşluk temizliği)
  * 🔍 Çift / Mükerrer kanalları ayıklama
* **📤 Çoklu Format Dışa Aktarma (Export):**
  * `📄 CSV (.csv)`: Excel ve LibreOffice Calc uyumlu tam parametre dökümü
  * `📝 TXT (.txt)`: Hizalanmış, yazdırılabilir temiz metin listesi
  * `📺 M3U (.m3u)`: VLC Player ve TVheadend için DVB-S URI parametreli oynatma listesi
* **📊 Dosya Karşılaştırma & Senkronizasyon (`Ctrl+K`):** İki `.sdx` listesini karşılaştırıp eklenen/silinen kanalları anında tespit etme.
* **📥 Başka Listeden Kanal İçe Aktarma (`Ctrl+I`):** Farklı bir listeden aranan kanalları seçip mevcut listeye aktarma.
* **🛡️ Emniyet Mekanizmaları:**
  * Otomatik emniyet yedeği (`.sdx.bak`)
  * SatcoDX 105 standartlarına %100 bayt uyumluluğu (Vestel, Toshiba, Regal, Hi-Level vb. TV donanımlarında test edilip onaylanmıştır).
* **⌨️ Klavye Kısayolları Kılavuzu (`Ctrl+/`):** Kategorize edilmiş hızlı başvuru penceresi.
* **🌐 Çoklu Dil Desteği:** Türkçe, English, Deutsch, Français, Español.
* **🎨 Modern Arayüz:** Karanlık ve Açık tema desteği.
* **🐧 Linux Entegrasyonu:** `.desktop` menü kısayolu, SVG ikonu, `.sdx` MIME dosya ilişkilendirmesi ve kurulum/kaldırma betikleri (`install_desktop.sh` / `uninstall_desktop.sh`).
