import logging
import asyncio
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime, timedelta
import threading
import json
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError

logging.basicConfig(
    filename='hata_kaydi.log',
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

class TelegramBotGUI:
    def __init__(self):
        self.pencere = tk.Tk()
        self.pencere.title("Telegram Bot Yönetim Paneli")
        self.pencere.geometry("900x700")
        self.pencere.configure(bg='#2b2b2b')
        
        self.bot_uygulamasi = None
        self.aktif_gruplar = []
        self.mesaj_listesi = []
        self.zamanlanmis_mesajlar = []
        self.bot_calisiyor = False
        self.telegram_token = "ekayazilim"
        self.hedef_mesaj_id = "ekayazilim"
        
        self.ayarlari_yukle()
        self.arayuz_olustur()
        
    def ayarlari_yukle(self):
        try:
            if os.path.exists('bot_ayarlari.json'):
                with open('bot_ayarlari.json', 'r', encoding='utf-8') as dosya:
                    veriler = json.load(dosya)
                    self.mesaj_listesi = veriler.get('mesaj_listesi', [])
                    self.zamanlanmis_mesajlar = veriler.get('zamanlanmis_mesajlar', [])
                    self.telegram_token = veriler.get('telegram_token', "8179822680:AAEeiRsg0vl-0qUIlShVejyBcKRNKYJf1uU")
                    self.hedef_mesaj_id = veriler.get('hedef_mesaj_id', "4087355")
        except Exception as hata:
            logger.error(f"Ayar yükleme hatası: {hata}")
    
    def ayarlari_kaydet(self):
        try:
            veriler = {
                'mesaj_listesi': self.mesaj_listesi,
                'zamanlanmis_mesajlar': self.zamanlanmis_mesajlar,
                'telegram_token': self.telegram_token,
                'hedef_mesaj_id': self.hedef_mesaj_id
            }
            with open('bot_ayarlari.json', 'w', encoding='utf-8') as dosya:
                json.dump(veriler, dosya, ensure_ascii=False, indent=2)
        except Exception as hata:
            logger.error(f"Ayar kaydetme hatası: {hata}")
    
    def arayuz_olustur(self):
        stil = ttk.Style()
        stil.theme_use('clam')
        stil.configure('TFrame', background='#2b2b2b')
        stil.configure('TLabel', background='#2b2b2b', foreground='white')
        stil.configure('TButton', background='#4a4a4a', foreground='white')
        
        ana_frame = ttk.Frame(self.pencere)
        ana_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        baslik_label = ttk.Label(ana_frame, text="Telegram Bot Kontrol Paneli", 
                                font=('Arial', 16, 'bold'))
        baslik_label.pack(pady=(0, 20))
        
        durum_frame = ttk.Frame(ana_frame)
        durum_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(durum_frame, text="Bot Durumu:").pack(side='left')
        self.durum_label = ttk.Label(durum_frame, text="Durduruldu", foreground='red')
        self.durum_label.pack(side='left', padx=(5, 0))
        
        self.bot_baslat_btn = ttk.Button(durum_frame, text="Bot Başlat", 
                                        command=self.bot_baslat)
        self.bot_baslat_btn.pack(side='right', padx=(5, 0))
        
        self.bot_durdur_btn = ttk.Button(durum_frame, text="Bot Durdur", 
                                        command=self.bot_durdur, state='disabled')
        self.bot_durdur_btn.pack(side='right')
        
        notebook = ttk.Notebook(ana_frame)
        notebook.pack(fill='both', expand=True)
        
        self.bot_ayarlari_sekmesi_olustur(notebook)
        self.mesaj_sekmesi_olustur(notebook)
        self.zamanlama_sekmesi_olustur(notebook)
        self.grup_sekmesi_olustur(notebook)
        self.log_sekmesi_olustur(notebook)
        
    def mesaj_sekmesi_olustur(self, notebook):
        mesaj_frame = ttk.Frame(notebook)
        notebook.add(mesaj_frame, text="Mesaj Yönetimi")
        
        ust_frame = ttk.Frame(mesaj_frame)
        ust_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(ust_frame, text="Yeni Mesaj:").pack(anchor='w')
        self.yeni_mesaj_text = scrolledtext.ScrolledText(ust_frame, height=4, width=60)
        self.yeni_mesaj_text.pack(fill='x', pady=(5, 0))
        
        buton_frame = ttk.Frame(ust_frame)
        buton_frame.pack(fill='x', pady=(5, 0))
        
        ttk.Button(buton_frame, text="Mesaj Ekle", command=self.mesaj_ekle).pack(side='left')
        ttk.Button(buton_frame, text="Seçili Sil", command=self.mesaj_sil).pack(side='left', padx=(5, 0))
        ttk.Button(buton_frame, text="Hemen Gönder", command=self.hemen_gonder).pack(side='right')
        
        ttk.Label(mesaj_frame, text="Mesaj Listesi:").pack(anchor='w', pady=(10, 5))
        
        liste_frame = ttk.Frame(mesaj_frame)
        liste_frame.pack(fill='both', expand=True)
        
        self.mesaj_listbox = tk.Listbox(liste_frame, bg='#3a3a3a', fg='white', 
                                       selectbackground='#4a90e2')
        scrollbar = ttk.Scrollbar(liste_frame, orient='vertical', command=self.mesaj_listbox.yview)
        self.mesaj_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.mesaj_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.mesaj_listesini_guncelle()
        
    def bot_ayarlari_sekmesi_olustur(self, notebook):
        ayar_frame = ttk.Frame(notebook)
        notebook.add(ayar_frame, text="Bot Ayarları")
        
        ttk.Label(ayar_frame, text="Telegram Bot Ayarları", font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        token_frame = ttk.Frame(ayar_frame)
        token_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(token_frame, text="Telegram Bot Token:").pack(anchor='w', pady=(0, 5))
        self.token_entry = tk.Entry(token_frame, width=60, font=('Courier', 9))
        self.token_entry.pack(fill='x')
        self.token_entry.insert(0, self.telegram_token)
        
        mesaj_id_frame = ttk.Frame(ayar_frame)
        mesaj_id_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(mesaj_id_frame, text="Hedef Mesaj ID (Opsiyonel):").pack(anchor='w', pady=(0, 5))
        self.mesaj_id_entry = tk.Entry(mesaj_id_frame, width=30)
        self.mesaj_id_entry.pack(anchor='w')
        self.mesaj_id_entry.insert(0, self.hedef_mesaj_id)
        
        buton_frame = ttk.Frame(ayar_frame)
        buton_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Button(buton_frame, text="Ayarları Kaydet", command=self.bot_ayarlarini_kaydet).pack(side='left')
        ttk.Button(buton_frame, text="Bot'u Yeniden Başlat", command=self.bot_yeniden_baslat).pack(side='left', padx=(10, 0))
        
        bilgi_frame = ttk.Frame(ayar_frame)
        bilgi_frame.pack(fill='both', expand=True, pady=(20, 0))
        
        ttk.Label(bilgi_frame, text="Bot Token Nasıl Alınır:", font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 10))
        
        bilgi_text = """1. Telegram'da @BotFather'ı bulun
2. /newbot komutunu gönderin
3. Bot adını ve kullanıcı adını girin
4. Size verilen token'ı yukarıdaki kutuya yapıştırın

Mesaj ID Nasıl Bulunur:
1. Telegram Web veya Desktop uygulamasını kullanın
2. Hedef sohbete gidin
3. URL'deki sayıları kopyalayın (örn: -1001234567890)"""
        
        info_label = tk.Label(bilgi_frame, text=bilgi_text, justify='left', 
                             bg='#2b2b2b', fg='#cccccc', font=('Arial', 9))
        info_label.pack(anchor='w', fill='both', expand=True)
        
    def bot_ayarlarini_kaydet(self):
        yeni_token = self.token_entry.get().strip()
        yeni_mesaj_id = self.mesaj_id_entry.get().strip()
        
        if not yeni_token:
            messagebox.showerror("Hata", "Bot token boş olamaz!")
            return
            
        if len(yeni_token.split(':')) != 2:
            messagebox.showerror("Hata", "Geçersiz bot token formatı!")
            return
            
        self.telegram_token = yeni_token
        self.hedef_mesaj_id = yeni_mesaj_id
        self.ayarlari_kaydet()
        
        messagebox.showinfo("Başarılı", "Bot ayarları kaydedildi! Değişikliklerin etkili olması için bot'u yeniden başlatın.")
        self.log_ekle("Bot ayarları güncellendi")
        
    def bot_yeniden_baslat(self):
        if self.bot_calisiyor:
            self.bot_durdur()
            threading.Timer(2.0, self.bot_baslat).start()
        else:
            self.bot_baslat()
        
    def zamanlama_sekmesi_olustur(self, notebook):
        zamanlama_frame = ttk.Frame(notebook)
        notebook.add(zamanlama_frame, text="Mesaj Zamanlama")
        
        ayar_frame = ttk.Frame(zamanlama_frame)
        ayar_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(ayar_frame, text="Gönderim Aralığı (dakika):").pack(anchor='w')
        self.aralik_spinbox = tk.Spinbox(ayar_frame, from_=1, to=1440, value=30, width=10)
        self.aralik_spinbox.pack(anchor='w', pady=(5, 10))
        
        ttk.Label(ayar_frame, text="Başlangıç Tarihi:").pack(anchor='w')
        tarih_frame = ttk.Frame(ayar_frame)
        tarih_frame.pack(anchor='w', pady=(5, 10))
        
        self.gun_spinbox = tk.Spinbox(tarih_frame, from_=1, to=31, value=datetime.now().day, width=3)
        self.gun_spinbox.pack(side='left')
        ttk.Label(tarih_frame, text="/").pack(side='left')
        
        self.ay_spinbox = tk.Spinbox(tarih_frame, from_=1, to=12, value=datetime.now().month, width=3)
        self.ay_spinbox.pack(side='left')
        ttk.Label(tarih_frame, text="/").pack(side='left')
        
        self.yil_spinbox = tk.Spinbox(tarih_frame, from_=2024, to=2030, value=datetime.now().year, width=5)
        self.yil_spinbox.pack(side='left')
        
        ttk.Label(ayar_frame, text="Başlangıç Saati:").pack(anchor='w')
        saat_frame = ttk.Frame(ayar_frame)
        saat_frame.pack(anchor='w', pady=(5, 10))
        
        self.saat_spinbox = tk.Spinbox(saat_frame, from_=0, to=23, value=datetime.now().hour, width=3)
        self.saat_spinbox.pack(side='left')
        ttk.Label(saat_frame, text=":").pack(side='left')
        
        self.dakika_spinbox = tk.Spinbox(saat_frame, from_=0, to=59, value=0, width=3)
        self.dakika_spinbox.pack(side='left')
        
        buton_frame = ttk.Frame(ayar_frame)
        buton_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(buton_frame, text="Zamanlamayı Başlat", command=self.zamanlamayi_baslat).pack(side='left')
        ttk.Button(buton_frame, text="Zamanlamayı Durdur", command=self.zamanlamayi_durdur).pack(side='left', padx=(5, 0))
        
        ttk.Label(zamanlama_frame, text="Zamanlanmış Mesajlar:").pack(anchor='w', pady=(20, 5))
        
        zamanlama_liste_frame = ttk.Frame(zamanlama_frame)
        zamanlama_liste_frame.pack(fill='both', expand=True)
        
        self.zamanlama_listbox = tk.Listbox(zamanlama_liste_frame, bg='#3a3a3a', fg='white')
        zamanlama_scrollbar = ttk.Scrollbar(zamanlama_liste_frame, orient='vertical', command=self.zamanlama_listbox.yview)
        self.zamanlama_listbox.configure(yscrollcommand=zamanlama_scrollbar.set)
        
        self.zamanlama_listbox.pack(side='left', fill='both', expand=True)
        zamanlama_scrollbar.pack(side='right', fill='y')
        
    def grup_sekmesi_olustur(self, notebook):
        grup_frame = ttk.Frame(notebook)
        notebook.add(grup_frame, text="Aktif Gruplar")
        
        # Manuel grup ekleme bölümü
        manuel_frame = ttk.Frame(grup_frame)
        manuel_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(manuel_frame, text="Manuel Grup Ekleme:", font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 10))
        
        id_frame = ttk.Frame(manuel_frame)
        id_frame.pack(fill='x', pady=(0, 5))
        
        ttk.Label(id_frame, text="Grup ID:").pack(side='left')
        self.manuel_grup_id_entry = tk.Entry(id_frame, width=20)
        self.manuel_grup_id_entry.pack(side='left', padx=(5, 10))
        
        ttk.Label(id_frame, text="Grup Adı:").pack(side='left')
        self.manuel_grup_adi_entry = tk.Entry(id_frame, width=30)
        self.manuel_grup_adi_entry.pack(side='left', padx=(5, 10))
        
        ttk.Button(id_frame, text="Grup Ekle", command=self.manuel_grup_ekle).pack(side='left', padx=(5, 0))
        
        # Bilgi metni
        bilgi_text = "Grup ID'si negatif sayı olmalıdır (örn: -1001234567890). Telegram Web'de grup URL'inden alabilirsiniz."
        ttk.Label(manuel_frame, text=bilgi_text, foreground='#cccccc', font=('Arial', 8)).pack(anchor='w')
        
        # Ayırıcı çizgi
        separator = ttk.Separator(grup_frame, orient='horizontal')
        separator.pack(fill='x', pady=(10, 10))
        
        ttk.Label(grup_frame, text="Bot'un Bulunduğu Gruplar:", font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 10))
        
        # Grup listesi frame'i
        liste_frame = ttk.Frame(grup_frame)
        liste_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        self.grup_listbox = tk.Listbox(liste_frame, bg='#3a3a3a', fg='white', height=12)
        grup_scrollbar = ttk.Scrollbar(liste_frame, orient='vertical', command=self.grup_listbox.yview)
        self.grup_listbox.configure(yscrollcommand=grup_scrollbar.set)
        
        self.grup_listbox.pack(side='left', fill='both', expand=True)
        grup_scrollbar.pack(side='right', fill='y')
        
        # Butonlar
        buton_frame = ttk.Frame(grup_frame)
        buton_frame.pack(fill='x')
        
        ttk.Button(buton_frame, text="Grupları Yenile", command=self.gruplari_yenile).pack(side='left')
        ttk.Button(buton_frame, text="Seçili Grubu Sil", command=self.secili_grup_sil).pack(side='left', padx=(10, 0))
        ttk.Button(buton_frame, text="Test Mesajı Gönder", command=self.test_mesaji_gonder).pack(side='right')
        
    def manuel_grup_ekle(self):
        grup_id = self.manuel_grup_id_entry.get().strip()
        grup_adi = self.manuel_grup_adi_entry.get().strip()
        
        if not grup_id or not grup_adi:
            messagebox.showwarning("Uyarı", "Grup ID ve adını giriniz!")
            return
            
        try:
            grup_id = int(grup_id)
            if grup_id > 0:
                messagebox.showwarning("Uyarı", "Grup ID negatif olmalı! (örn: -1001234567890)")
                return
                
            # Grup zaten var mı kontrol et
            for grup in self.aktif_gruplar:
                if grup['id'] == grup_id:
                    messagebox.showwarning("Uyarı", "Bu grup zaten listede!")
                    return
                    
            # Yeni grubu ekle
            self.aktif_gruplar.append({
                'id': grup_id,
                'title': grup_adi,
                'type': 'manuel'
            })
            
            self.gruplari_yenile()
            self.manuel_grup_id_entry.delete(0, 'end')
            self.manuel_grup_adi_entry.delete(0, 'end')
            
            self.log_ekle(f"Manuel grup eklendi: {grup_adi} (ID: {grup_id})")
            messagebox.showinfo("Başarılı", f"Grup eklendi: {grup_adi}")
            
        except ValueError:
            messagebox.showerror("Hata", "Geçersiz grup ID! Sayı giriniz.")
            
    def secili_grup_sil(self):
        secili = self.grup_listbox.curselection()
        if secili:
            indeks = secili[0]
            silinen_grup = self.aktif_gruplar.pop(indeks)
            self.gruplari_yenile()
            self.log_ekle(f"Grup silindi: {silinen_grup['title']}")
        else:
            messagebox.showwarning("Uyarı", "Lütfen silinecek grubu seçin!")
            
    def test_mesaji_gonder(self):
        if not self.aktif_gruplar:
            messagebox.showwarning("Uyarı", "Aktif grup bulunamadı!")
            return
            
        if not self.bot_calisiyor:
            messagebox.showwarning("Uyarı", "Bot çalışmıyor! Önce bot'u başlatın.")
            return
            
        test_mesaji = f"🤖 Test mesajı - {datetime.now().strftime('%H:%M:%S')}"
        self.mesaji_gonder_async(test_mesaji)
        self.log_ekle("Test mesajı gönderildi")
        
    def log_sekmesi_olustur(self, notebook):
        log_frame = ttk.Frame(notebook)
        notebook.add(log_frame, text="Sistem Logları")
        
        self.log_text = scrolledtext.ScrolledText(log_frame, bg='#1a1a1a', fg='white', height=20)
        self.log_text.pack(fill='both', expand=True, pady=(0, 10))
        
        ttk.Button(log_frame, text="Logları Temizle", command=self.loglari_temizle).pack()
        
        self.log_ekle("Program başlatıldı")
        
    def mesaj_ekle(self):
        mesaj = self.yeni_mesaj_text.get('1.0', 'end-1c').strip()
        if mesaj:
            self.mesaj_listesi.append(mesaj)
            self.mesaj_listesini_guncelle()
            self.yeni_mesaj_text.delete('1.0', 'end')
            self.ayarlari_kaydet()
            self.log_ekle(f"Yeni mesaj eklendi: {mesaj[:50]}...")
        else:
            messagebox.showwarning("Uyarı", "Lütfen bir mesaj yazın!")
            
    def mesaj_sil(self):
        secili = self.mesaj_listbox.curselection()
        if secili:
            indeks = secili[0]
            silinen = self.mesaj_listesi.pop(indeks)
            self.mesaj_listesini_guncelle()
            self.ayarlari_kaydet()
            self.log_ekle(f"Mesaj silindi: {silinen[:50]}...")
        else:
            messagebox.showwarning("Uyarı", "Lütfen silinecek mesajı seçin!")
            
    def mesaj_listesini_guncelle(self):
        self.mesaj_listbox.delete(0, 'end')
        for i, mesaj in enumerate(self.mesaj_listesi):
            ozet = mesaj[:80] + "..." if len(mesaj) > 80 else mesaj
            self.mesaj_listbox.insert('end', f"{i+1}. {ozet}")
            
    def hemen_gonder(self):
        if not self.aktif_gruplar:
            messagebox.showwarning("Uyarı", "Aktif grup bulunamadı! Bot'u bir gruba ekleyin.")
            return
            
        if not self.bot_calisiyor:
            messagebox.showwarning("Uyarı", "Bot çalışmıyor! Önce bot'u başlatın.")
            return
            
        secili = self.mesaj_listbox.curselection()
        if secili:
            mesaj = self.mesaj_listesi[secili[0]]
            self.mesaji_gonder_async(mesaj)
            self.log_ekle("Mesaj gönderme işlemi başlatıldı...")
        else:
            messagebox.showwarning("Uyarı", "Lütfen gönderilecek mesajı seçin!")
            
    def mesaji_gonder_async(self, mesaj):
        def gonder_threaded():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.mesaji_gonder_calistir(mesaj))
            finally:
                loop.close()
        
        threading.Thread(target=gonder_threaded, daemon=True).start()
    
    async def mesaji_gonder_calistir(self, mesaj):
        try:
            basarili_grup_sayisi = 0
            for grup in self.aktif_gruplar:
                try:
                    await self.bot_uygulamasi.bot.send_message(chat_id=grup['id'], text=mesaj)
                    basarili_grup_sayisi += 1
                    await asyncio.sleep(1)
                except Exception as grup_hata:
                    self.pencere.after(0, lambda: self.log_ekle(f"Grup {grup['title']} hata: {grup_hata}"))
            
            self.pencere.after(0, lambda: self.log_ekle(f"Mesaj {basarili_grup_sayisi} gruba başarıyla gönderildi"))
            
        except Exception as hata:
            self.pencere.after(0, lambda: self.log_ekle(f"Mesaj gönderim hatası: {hata}"))
            logger.error(f"Mesaj gönderim hatası: {hata}")
            
    def zamanlamayi_baslat(self):
        if not self.mesaj_listesi:
            messagebox.showwarning("Uyarı", "Mesaj listesi boş!")
            return
            
        try:
            gun = int(self.gun_spinbox.get())
            ay = int(self.ay_spinbox.get())
            yil = int(self.yil_spinbox.get())
            saat = int(self.saat_spinbox.get())
            dakika = int(self.dakika_spinbox.get())
            aralik = int(self.aralik_spinbox.get())
            
            baslangic = datetime(yil, ay, gun, saat, dakika)
            
            if baslangic <= datetime.now():
                messagebox.showwarning("Uyarı", "Başlangıç zamanı geçmişte olamaz!")
                return
                
            self.zamanlama_gorevi_olustur(baslangic, aralik)
            self.log_ekle(f"Zamanlama başlatıldı - Başlangıç: {baslangic}, Aralık: {aralik} dakika")
            
        except ValueError:
            messagebox.showerror("Hata", "Geçersiz tarih/saat formatı!")
            
    def zamanlama_gorevi_olustur(self, baslangic_zamani, aralik_dakika):
        def zamanlama_gorevi():
            mesaj_indeksi = 0
            simdiki_zaman = baslangic_zamani
            
            while True:
                try:
                    if datetime.now() >= simdiki_zaman:
                        if self.aktif_gruplar and self.mesaj_listesi:
                            mesaj = self.mesaj_listesi[mesaj_indeksi % len(self.mesaj_listesi)]
                            self.mesaji_gonder_async(mesaj)
                            
                            mesaj_indeksi += 1
                            simdiki_zaman += timedelta(minutes=aralik_dakika)
                            
                            self.pencere.after(0, lambda m=mesaj: self.log_ekle(f"Zamanlanmış mesaj gönderildi: {m[:30]}..."))
                        
                    threading.Event().wait(60)
                    
                except Exception as hata:
                    self.pencere.after(0, lambda h=hata: self.log_ekle(f"Zamanlama hatası: {h}"))
                    logger.error(f"Zamanlama hatası: {hata}")
                    break
                    
        threading.Thread(target=zamanlama_gorevi, daemon=True).start()
        
    def zamanlamayi_durdur(self):
        self.log_ekle("Zamanlama durduruldu")
        
    def gruplari_yenile(self):
        self.grup_listbox.delete(0, 'end')
        for i, grup in enumerate(self.aktif_gruplar):
            grup_tipi = ""
            if grup.get('type') == 'manuel':
                grup_tipi = " [Manuel]"
            elif grup.get('type') == 'private':
                grup_tipi = " [Özel]"
            elif grup.get('type') in ['group', 'supergroup']:
                grup_tipi = " [Grup]"
                
            liste_metni = f"{grup['title']}{grup_tipi} (ID: {grup['id']})"
            self.grup_listbox.insert('end', liste_metni)
            
    def log_ekle(self, mesaj):
        zaman = datetime.now().strftime("%H:%M:%S")
        log_metni = f"[{zaman}] {mesaj}\n"
        self.log_text.insert('end', log_metni)
        self.log_text.see('end')
        
    def loglari_temizle(self):
        self.log_text.delete('1.0', 'end')
        
    async def baslat_komutu(self, guncelleme: Update, baglam: ContextTypes.DEFAULT_TYPE):
        try:
            chat = guncelleme.effective_chat
            await guncelleme.message.reply_text("Bot çalışıyor ve kontrol paneli aktif!")
            
            # Grup bilgisini hemen ekle
            grup_mevcut = False
            for grup in self.aktif_gruplar:
                if grup['id'] == chat.id:
                    grup_mevcut = True
                    break
                    
            if not grup_mevcut:
                chat_title = chat.title if chat.title else f"Kullanıcı: {chat.first_name or 'Bilinmeyen'}"
                self.aktif_gruplar.append({
                    'id': chat.id,
                    'title': chat_title,
                    'type': chat.type
                })
                self.pencere.after(0, self.gruplari_yenile)
                self.pencere.after(0, lambda: self.log_ekle(f"Yeni sohbet eklendi: {chat_title} (ID: {chat.id})"))
                
        except Exception as hata:
            logger.error(f"baslat_komutu hatası: {hata}")
            
    async def gruplar_komutu(self, guncelleme: Update, baglam: ContextTypes.DEFAULT_TYPE):
        try:
            chat = guncelleme.effective_chat
            chat_info = f"Sohbet Bilgisi:\nID: {chat.id}\nTür: {chat.type}\nBaşlık: {chat.title or 'Yok'}"
            await guncelleme.message.reply_text(chat_info)
            
            # Bu sohbeti de listeye ekle
            grup_mevcut = False
            for grup in self.aktif_gruplar:
                if grup['id'] == chat.id:
                    grup_mevcut = True
                    break
                    
            if not grup_mevcut:
                chat_title = chat.title if chat.title else f"Kullanıcı: {chat.first_name or 'Bilinmeyen'}"
                self.aktif_gruplar.append({
                    'id': chat.id,
                    'title': chat_title,
                    'type': chat.type
                })
                self.pencere.after(0, self.gruplari_yenile)
                self.pencere.after(0, lambda: self.log_ekle(f"Sohbet bilgisi alındı: {chat_title}"))
                
        except Exception as hata:
            logger.error(f"gruplar_komutu hatası: {hata}")
            
    async def mesaj_yakalayici(self, guncelleme: Update, baglam: ContextTypes.DEFAULT_TYPE):
        try:
            chat = guncelleme.effective_chat
            
            grup_mevcut = False
            for grup in self.aktif_gruplar:
                if grup['id'] == chat.id:
                    grup_mevcut = True
                    break
                    
            if not grup_mevcut and chat.type in ['group', 'supergroup']:
                self.aktif_gruplar.append({
                    'id': chat.id,
                    'title': chat.title or "Bilinmeyen Grup"
                })
                self.pencere.after(0, self.gruplari_yenile)
                self.pencere.after(0, lambda: self.log_ekle(f"Yeni grup eklendi: {chat.title}"))
                
            kullanici_mesaji = guncelleme.message.text
            await guncelleme.message.reply_text(f"Echo: {kullanici_mesaji}")
            
        except Exception as hata:
            logger.error(f"mesaj_yakalayici hatası: {hata}")
            
    def bot_baslat(self):
        if not self.telegram_token:
            self.log_ekle("Bot token bulunamadı!")
            messagebox.showerror("Hata", "Lütfen önce bot token'ını girin!")
            return
            
        def bot_calistir():
            try:
                asyncio.set_event_loop(asyncio.new_event_loop())
                
                self.bot_uygulamasi = Application.builder().token(self.telegram_token).build()
                
                self.bot_uygulamasi.add_handler(CommandHandler("baslat", self.baslat_komutu))
                self.bot_uygulamasi.add_handler(CommandHandler("gruplar", self.gruplar_komutu))
                self.bot_uygulamasi.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.mesaj_yakalayici))
                
                self.bot_calisiyor = True
                self.pencere.after(0, lambda: self.durum_guncelle("Çalışıyor", "green"))
                self.pencere.after(0, lambda: self.bot_durdur_btn.config(state='normal'))
                self.pencere.after(0, lambda: self.bot_baslat_btn.config(state='disabled'))
                self.pencere.after(0, lambda: self.log_ekle("Telegram bot başarıyla başlatıldı"))
                
                self.bot_uygulamasi.run_polling(allowed_updates=Update.ALL_TYPES)
                
            except Exception as hata:
                self.bot_calisiyor = False
                self.pencere.after(0, lambda: self.durum_guncelle("Hata", "red"))
                self.pencere.after(0, lambda: self.bot_baslat_btn.config(state='normal'))
                self.pencere.after(0, lambda: self.log_ekle(f"Bot başlatma hatası: {hata}"))
                logger.error(f"Bot başlatma hatası: {hata}")
                
        threading.Thread(target=bot_calistir, daemon=True).start()
        
    def bot_durdur(self):
        try:
            if self.bot_uygulamasi:
                self.bot_uygulamasi.stop_running()
                self.bot_calisiyor = False
                self.durum_guncelle("Durduruldu", "red")
                self.bot_durdur_btn.config(state='disabled')
                self.bot_baslat_btn.config(state='normal')
                self.log_ekle("Bot durduruldu")
        except Exception as hata:
            self.log_ekle(f"Bot durdurma hatası: {hata}")
            
    def durum_guncelle(self, durum, renk):
        self.durum_label.config(text=durum, foreground=renk)
        
    def pencere_kapat(self):
        self.ayarlari_kaydet()
        if self.bot_calisiyor:
            self.bot_durdur()
        self.pencere.destroy()
        
    def calistir(self):
        self.pencere.protocol("WM_DELETE_WINDOW", self.pencere_kapat)
        self.pencere.mainloop()

if __name__ == '__main__':
    uygulama = TelegramBotGUI()

    uygulama.calistir()
