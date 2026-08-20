# 🧪 SatSort Manuel Doğrulama ve Test Planı

SatSort uygulamasının tüm özelliklerini uçtan uca test etmeniz için hazırlanmış aşamalı kontrol listesidir. Lütfen bu adımları kendi ortamınızda sırasıyla deneyiniz.

## Aşama 1: Başlangıç ve Temel Dosya İşlemleri
- [x] Terminalden `python3 main.py` komutuyla uygulamayı başlatın.
- [x] Uygulamanın sorunsuz bir şekilde açıldığını doğrulayın.
- [x] **Dosya Aç:** Menüden veya araç çubuğundan `Dosya -> Aç` diyerek elinizdeki geçerli bir `.sdx` dosyasını (örneğin `sample_turksat.sdx`) yükleyin.
- [x] Kanalların tabloya doğru sıralama, doğru isim ve tiplerle (TV/Radyo/Data) geldiğini kontrol edin.

## Aşama 2: Tablo Etkileşimleri ve Düzenleme
- [!] ⚠️ **Sürükle ve Bırak (Drag & Drop):** Tablodan bir veya birkaç kanalı fareyle tutup başka bir satıra sürükleyerek bırakın. *(İyileştirme planına alındı: Çoklu taşıma & hedef göstergesi)*
- [x] **Kanal Adı Değiştirme:** Bir kanala çift tıklayın (veya sağ tık menüsünden "Kanal Adını Değiştir" seçin). En fazla 16 karakter sınırı uygulandığını ve kural dışı karakter girişinin engellendiğini görün.
- [!] ⚠️ **Canlı Arama:** Araç çubuğundaki arama kutusuna (Örn: "TRT") yazın. *(İyileştirme planına alındı: Önceki/Sonraki butonları & Scrollbar işaretçileri)*
- [!] ⚠️ **Sağ Tık Menüsü:** Kanallara sağ tıklayıp "Yukarı Taşı", "Aşağı Taşı", "Takas Et" gibi işlemleri deneyerek doğru çalıştığını doğrulayın. *(İyileştirme planına alındı: Takas indeksi düzeltmesi)*
- [!] ⚠️ **Çoklu İşlemler:** `Ctrl` veya `Shift` basılı tutarak veya kutucukları (checkbox) kullanarak birden fazla kanalı seçin, işaretleyin ve silme işlemini test edin. *(İyileştirme planına alındı: Akıllı silme & dinamik sağ tık menüsü)*

## Aşama 3: Paneller ve Diyalog Pencereleri
- [x] **Sağ Detay Paneli (Sidebar):** Bir kanala tıkladığınızda pencerenin sağında o kanalın teknik değerlerinin (Frekans, Pol, SR, vb.) güncellendiğinden emin olun.
- [x] **Transponder Paketi:** Sağ panelin altındaki listede, seçtiğiniz kanalla **aynı frekans ve polarizasyona** sahip paket içi diğer kanalların listelendiğini kontrol edin. Listeden birine tıklayıp tabloda ona atlayabildiğinizi doğrulayın.
- [x] **Farklı Dosyadan Kopyalama:** Araç çubuğundan "İçe Aktar" ikonuna tıklayın. Başka bir `.sdx` dosyası seçip içinden birkaç kanal işaretleyerek mevcut listenize hatasız şekilde eklendiğini doğrulayın.
- [!] ⚠️ **İki Dosya Karşılaştırma:** Menüden "Karşılaştır" diyerek eski ve yeni liste arasında silinen/eklenen kanalların raporunu alın. *(İyileştirme planına alındı: Gelişmiş sıra/isim/kanal diff motoru)*
- [!] ⚠️ **Dil Değiştirme:** `Görünüm -> Dil Seçimi` menüsünden dili İngilizceye alıp arayüzün anında çevrildiğini gözlemleyin. *(İyileştirme planına alındı: Canlı retranslate_ui altyapısı)*

## Aşama 4: Kaydetme ve Gerçek Cihaz (Hardware) Doğrulaması
> [!IMPORTANT]
> Bu aşama, uygulamanın ürettiği dosya formatının hedef cihazla tamamen uyumlu çalıştığını kanıtlayan en kritik testtir.

- [ ] Yaptığınız tüm düzenleme ve sıralamaların ardından `Dosya -> Farklı Kaydet` diyerek yeni bir `.sdx` dosyası oluşturun.
- [ ] Oluşturulan bu dosyayı bir USB belleğe (veya cihazın desteklediği birime) aktarın.
- [ ] USB belleği uydu alıcısına (Set-top box) takın ve cihazın menüsünden kanal yükleme işlemini başlatın.
- [ ] Cihazın dosyayı tanıyıp başarıyla okuduğunu, hata vermediğini ve televizyonda kanalların bilgisayarda yaptığınız sırayla ve yeni isimleriyle geldiğini onaylayın.
