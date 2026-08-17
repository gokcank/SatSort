# 🛰️ SatSort

**SatSort**, uydu alıcıları için standart **SatcoDX (`.sdx`)** formatındaki kanal listelerini Linux üzerinde hızlı, görsel ve modern bir arayüzle düzenleme, sıralama, arama ve senkronize etme aracıdır.

---

## ✨ Özellikler

* **🖱️ Sürükle-Bırak (Drag & Drop) Sıralama:** Fareyle kanalların sırasını tek tek veya topluca kolayca değiştirin.
* **🔍 Canlı Arama ve Hızlı Seçim:** Anlık kanal arama, eşleşen kanal sayacı ve `Enter` ile bulunan kanalları otomatik işaretleme.
* **📑 Teknik Detay & Transponder Paneli:** Seçilen kanalın tüm frekans, polarizasyon, sembol oranı, FEC ve PID (VPID, APID, PCRP, SID, NID, TSID) parametrelerini inceleyin ve aynı paketteki diğer kanalları listeleyin.
* **📊 İki Dosyayı Karşılaştırma:** Farklı iki `.sdx` dosyasını karşılaştırıp **Silinen Kanallar** ve **Yeni Eklenen Kanallar** listesini çıkarın, tek tıkla senkronize edin.
* **📥 Başka Dosyadan Kanal Kopyalama:** İkinci bir `.sdx` dosyasını açıp aradığınız kanalları seçerek mevcut listenize aktarın.
* **🌐 Çoklu Dil Desteği:** Türkçe, English, Deutsch, Français ve Español dilleri arasında anında geçiş yapın.
* **🎨 Modern Linux Karanlık Tema:** Göz yormayan, modern masaüstü tasarımına uygun şık karanlık arayüz.
* **🔒 Standart Uyumluluğu:** Orijinal `.sdx` sabit genişlikli sütun yapısını ve dosya sonu null (`\0`) bayt kurallarını %100 korur.

---

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler
* Python 3.8 veya üzeri
* PySide6 (Qt6)

### Kurulum Adımları
```bash
# Depoyu klonlayın
git clone <repo-url>
cd SatSort

# Sanal ortam oluşturun (isteğe bağlı)
python3 -m venv .venv
source .venv/bin/activate

# Bağımlılıkları yükleyin
pip install -r requirements.txt
```

### Uygulamayı Başlatma
```bash
# Ana uygulamayı başlatın
python3 main.py

# Doğrudan bir .sdx dosyası açarak başlatmak için:
python3 main.py /path/to/kanallar.sdx
```

---

## 🧪 Testleri Çalıştırma

Tüm birim ve entegrasyon testlerini çalıştırmak için:
```bash
python3 -m unittest discover tests
```

---

## 📜 Lisans & Esinlenme

Bu proje [MIT Lisansı](LICENSE) altında açık kaynak olarak dağıtılmaktadır.

> **Atıf ve Teşekkür:**  
> Bu proje, **Mehmet Taşköprü** tarafından geliştirilen açık kaynaklı [NovaSatcoDX](https://sourceforge.net/projects/novasatcodx/) Windows projesinden esinlenilerek, Linux platformu için sıfırdan modern Python & Qt6 (PySide6) mimarisiyle yeniden geliştirilmiştir.
