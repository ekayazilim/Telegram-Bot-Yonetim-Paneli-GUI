# 🤖 Telegram Bot Yönetim Paneli (GUI)

Bu proje, **Python + Tkinter** kullanılarak geliştirilmiş, **Telegram botlarını görsel bir arayüz üzerinden yönetmenizi** sağlayan kapsamlı bir masaüstü uygulamasıdır.

Mesaj gönderme, zamanlama, grup yönetimi ve bot ayarları tek bir panel üzerinden kolay ve stabil şekilde yapılabilir.

Geliştirici: **Eka Yazılım ve Bilişim Sistemleri**

---

## 🚀 Özellikler

* Telegram botunu GUI üzerinden başlatma ve durdurma
* Bot token ve hedef sohbet / grup ID yönetimi
* Mesaj ekleme, silme ve anında gönderme
* Belirli tarih ve saatten itibaren periyodik mesaj gönderimi
* Botun bulunduğu grupları otomatik algılama
* Manuel grup ekleme ve silme
* Test mesajı gönderme
* Canlı sistem logları
* Ayarları JSON dosyasında saklama
* Çoklu grup desteği
* Thread ve asyncio destekli donmayan arayüz

---

## 🖥️ Arayüz Sekmeleri

### Bot Ayarları

* Telegram Bot Token tanımlama
* Hedef mesaj veya grup ID belirleme
* Bot ayarlarını kaydetme ve yeniden başlatma

### Mesaj Yönetimi

* Mesaj listesi oluşturma
* Mesaj silme
* Seçili mesajı anında gönderme

### Mesaj Zamanlama

* Başlangıç tarihi ve saati
* Gönderim aralığı (dakika bazlı)
* Döngüsel mesaj gönderimi

### Aktif Gruplar

* Otomatik grup algılama
* Manuel grup ekleme
* Grup silme
* Test mesajı gönderme

### Sistem Logları

* Gerçek zamanlı işlem kayıtları
* Log temizleme

---

## 📂 Dosya Yapısı

```
proje_klasoru
│
├── main.py
├── bot_ayarlari.json
├── hata_kaydi.log
```

---

## ⚙️ Gereksinimler

* Python 3.9 veya üzeri
* Gerekli kütüphaneler:

  * python-telegram-bot
  * tkinter (Python ile birlikte gelir)

---

## 📦 Kurulum

```bash
pip install python-telegram-bot==20.7
```

---

## ▶️ Çalıştırma

```bash
python main.py
```

Uygulama açıldıktan sonra:

1. Bot Ayarları sekmesinden Telegram Bot Token girin
2. Botu **Başlat** butonu ile çalıştırın
3. Botu Telegram’da bir gruba ekleyin
4. Telegram üzerinden `/baslat` komutunu gönderin
5. Gruplar otomatik olarak panele eklenecektir

---

## 🔐 Telegram Bot Token Alma

1. Telegram’da **@BotFather** hesabını açın
2. `/newbot` komutunu gönderin
3. Bot adı ve kullanıcı adını belirleyin
4. Verilen token’ı panele yapıştırın

---

## 🧠 Teknik Detaylar

* asyncio ve threading birlikte kullanılarak arayüzün donması engellenmiştir
* Mesaj gönderimleri Telegram API limitlerine uygun gecikmelerle yapılır
* Ayarlar `bot_ayarlari.json` dosyasında saklanır
* Hatalar `hata_kaydi.log` dosyasına kaydedilir

---


## 📜 Lisans

Bu proje eğitim ve ticari kullanım için uygundur.
İzinsiz satışı ve dağıtımı yasaktır.

© Eka Yazılım ve Bilişim Sistemleri
