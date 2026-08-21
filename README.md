# 🛰️ SatSort

[![SatSort CI](https://github.com/gokcank/SatSort/actions/workflows/ci.yml/badge.svg)](https://github.com/gokcank/SatSort/actions/workflows/ci.yml)
[![GitHub release](https://img.shields.io/github/v/release/gokcank/SatSort?color=38bdf8)](https://github.com/gokcank/SatSort/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: >=3.8](https://img.shields.io/badge/Python->=3.8-blue.svg)](https://www.python.org/)
[![GUI: Qt6 / PySide6](https://img.shields.io/badge/GUI-Qt6%20%2F%20PySide6-green.svg)](https://wiki.qt.io/Qt_for_Python)

**SatSort**, uydu alıcıları ve akıllı televizyonlar (Vestel, Toshiba, Regal, Hi-Level, Telefunken, JVC, Finlux, Techwood vb.) için standart **SatcoDX (`.sdx`)** formatındaki kanal listelerini Linux üzerinde modern, hızlı ve görsel bir arayüzle düzenleme, sıralama, arama, temizleme ve dışa aktarma aracıdır.

---

## ✨ Temel Özellikler

* **🖱️ Sürükle-Bırak & Araya Ekle/Kaydır (Insert & Shift):** Kanalları fareyle taşıyın veya klavyeden (`Alt+Up/Down`) sıra kayması riski olmadan araya ekleyip diğer kanalları aşağı kaydırın.
* **🎯 Numaraya Taşı (`Ctrl+M`):** Kanal numarasını girerek kanalı anında istediğiniz sıraya taşıyın.
* **🔗 Referans Liste ile Sıralama:** Eski/düzenli bir `.sdx` dosyasını referans seçerek, TV'den yeni taranmış yüzlerce kanalı tek tıkla eski sıralamanıza otomatik dizin.
* **🧹 Akıllı Toplu Temizlik Araçları:**
  * 📻 **Radyoları Listenin Sonuna Taşı**
  * 🔒 **Şifreli Kanalları Sil**
  * 🔤 **Kanal İsimlerini Standartlaştır (Büyük Harf & Fazlalık Boşluk Temizliği)**
  * 🔍 **Çift / Mükerrer Kanalları Ayıkla**
* **📤 Çoklu Format Dışa Aktarma (Export):**
  * `📄 CSV (.csv)`: Excel ve LibreOffice Calc uyumlu döküm.
  * `📝 TXT (.txt)`: Hizalanmış, yazdırılabilir metin tablosu.
  * `📺 M3U (.m3u)`: VLC Player ve TVheadend için DVB-S URI destekli oynatma listesi.
* **🔍 Canlı Arama & Hızlı Seçim:** Anlık kanal arama, eşleşen kanal sayacı ve `Enter` ile bulunan kanalları otomatik işaretleme.
* **📊 İki Dosyayı Karşılaştırma (`Ctrl+K`):** İki `.sdx` listesini karşılaştırıp silinen ve yeni eklenen kanalları anında tespit edin.
* **📥 Başka Dosyadan Kanal Kopyalama (`Ctrl+I`):** İkinci bir dosyadan aradığınız kanalları seçip mevcut listenize aktarın.
* **🛡️ Emniyet Mekanizmaları:** Otomatik `.sdx.bak` yedekleme ve SatcoDX 105 standartlarına %100 bayt uyumluluğu.
* **🌐 Çoklu Dil:** Türkçe, English, Deutsch, Français, Español.
* **🎨 Modern Arayüz:** Karanlık ve Açık tema desteği.

---

## 📦 İndirme ve Kurulum

### 🌟 1. APT Deposu ile Kurulum (Ubuntu / Debian / Pardus / Linux Mint)
En kolay yöntemdir. SatSort'u tek komutla kurabilir ve sistem güncellemeleriyle (`sudo apt upgrade`) otomatik olarak yeni sürümleri alabilirsiniz:

```bash
# 1. SatSort APT deposunu ekleyin
echo "deb [trusted=yes] https://gokcank.github.io/SatSort stable main" | sudo tee /etc/apt/sources.list.d/satsort.list

# 2. Paket listesini güncelleyip SatSort'u kurun
sudo apt update
sudo apt install satsort
```

---

### 🚀 2. Evrensel Linux Paketi: AppImage (Kurulumsuz)
Hiçbir kurulum veya ek kütüphane gerektirmez. Ubuntu, Debian, Fedora, Arch, Manjaro, Linux Mint vb. tüm dağıtımlarda çalışır:
```bash
# Çalıştırma izni verip doğrudan açın
chmod +x SatSort-1.0.0-x86_64.AppImage
./SatSort-1.0.0-x86_64.AppImage
```

### 🐧 3. Doğrudan `.deb` Paketi İndirip Kurma
```bash
sudo dpkg -i satsort_1.0.0_amd64.deb
```

### ⚡ 4. Taşınabilir Tek Dosya Binary
```bash
chmod +x satsort-linux-x86_64
./satsort-linux-x86_64
```

---

## 🛠️ Kaynak Koddan Çalıştırma

```bash
# Depoyu klonlayın
git clone https://github.com/gokcank/SatSort.git
cd SatSort

# Sanal ortam oluşturun ve bağımlılıkları yükleyin
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Uygulamayı başlatın
python3 main.py

# Doğrudan bir kanal dosyasıyla başlatmak için:
python3 main.py /path/to/kanallar.sdx
```

### Masaüstü Entegrasyonu:
Sistem menüsüne ve `.sdx` dosya çift tıklama ilişkilendirmesine kurmak için:
```bash
./install_desktop.sh
```

---

## ⌨️ Klavye Kısayolları

| Kısayol | İşlev |
| :--- | :--- |
| `Ctrl + O` | Dosya Aç (`.sdx`) |
| `Ctrl + S` | Değişiklikleri Kaydet |
| `Ctrl + M` | Kanalı Numaraya Taşı (Araya Ekle & Kaydır) |
| `Alt + Up / Down` | Seçili Kanalı 1 Sıra Yukarı/Aşağı Taşı |
| `F2` | Kanalı Yeniden Adlandır |
| `Space` | Kanal İşaretini Aç/Kapat (Checkbox) |
| `Delete` | Seçili / İşaretli Kanalları Sil |
| `Ctrl + A` | Tüm Kanalları İşaretle |
| `Ctrl + F` | Arama Çubuğuna Odaklan |
| `F4` | Sağ Bilgi Panelini Aç/Kapat |
| `Ctrl + K` | İki Listeyi Karşılaştır |
| `Ctrl + I` | Farklı Dosyadan Kanal İçe Aktar |
| `Ctrl + /` | Klavye Kısayolları Kılavuzu |
| `F1` | SatSort Hakkında |

---

## 🧪 Testleri Çalıştırma

Tüm test paketini çalıştırmak için:
```bash
python3 -m unittest discover tests
```

---

## 📜 Lisans & Teşekkür

Bu proje [MIT Lisansı](LICENSE) altında açık kaynak olarak dağıtılmaktadır.

* **Geliştirici:** [Gökcan](https://github.com/gokcank)
* **Atıf ve Esinlenme:** Bu proje, **Mehmet Taşköprü** tarafından geliştirilen açık kaynaklı [NovaSatcoDX](https://sourceforge.net/projects/novasatcodx/) projesinden esinlenilerek, Linux platformu için sıfırdan modern Python & Qt6 mimarisiyle geliştirilmiştir.
