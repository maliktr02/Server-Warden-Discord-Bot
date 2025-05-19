# ServerWarden Discord Bot

ServerWarden, Discord sunucuları için gelişmiş moderasyon ve yönetim özellikleri sunan bir bottur.

## Özellikler

### Temel Özellikler
- Çekiliş yapabilme
- Kullanıcıyı mute atma
- Kullanıcıyı ban atma
- Kullanıcıyı sunucudan atma
- Caps lock engelleme
- Flood engelleme
- Yasaklı kelime tespiti
- Yasaklı kelimeye otomatik mute
- Gelen mesaj bildirimi
- Giden mesaj bildirimi
- Uyarı atabilme
- Uyarı listesini görebilme
- ! ile Türkçe komut desteği
- Avatar gösterme
- Yazı tura komutu
- Oylama başlatma

### Premium Özellikler (Aylık 1.99$)
- Gelişmiş çekiliş (!çekiliş_turbo)
- Gelişmiş log sistemi
- Sunucu istatistik paneli
- Otomatik rol atama
- Komut özelleştirme (!komut_özelleştir)
- Otomatik yedekleme
- Gizli premium komutlar
- Profil komutu
- Sunucu bilgisi gösterme
- Uyarı süresine göre otomatik unmute
- Zamanlayıcı sistem

## Kurulum

1. Python 3.8 veya daha yüksek bir sürümü yükleyin.
2. MongoDB veritabanı kurulumu yapın ve bir veritabanı oluşturun.
3. Gerekli paketleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
4. `.env` dosyası oluşturun ve aşağıdaki değişkenleri ekleyin:
   ```
   DISCORD_TOKEN=your_discord_bot_token
   MONGODB_URI=your_mongodb_connection_string
   ```
5. Botu çalıştırın:
   ```bash
   python bot.py
   ```

## Komutlar

### Temel Komutlar
- `!çekiliş <süre> <ödül>` - Çekiliş başlatır
- `!mute <@kullanıcı> [süre] [sebep]` - Kullanıcıyı mute atar
- `!ban <@kullanıcı> [sebep]` - Kullanıcıyı banlar
- `!kick <@kullanıcı> [sebep]` - Kullanıcıyı sunucudan atar
- `!uyarı <@kullanıcı> [sebep]` - Kullanıcıya uyarı verir
- `!uyarılar [@kullanıcı]` - Uyarıları gösterir
- `!avatar [@kullanıcı]` - Avatarı gösterir
- `!yazıtura` - Yazı tura atar
- `!oylama <soru>` - Oylama başlatır

### Premium Komutlar
- `!çekiliş_turbo <süre> <kazanan_sayısı> <ödül>` - Gelişmiş çekiliş başlatır
- `!sunucu_bilgi` - Sunucu istatistiklerini gösterir
- `!rol_ata <@rol>` - Yeni üyelere otomatik rol atar
- `!komut_özelleştir <komut_adı> <yanıt>` - Komut yanıtlarını özelleştirir
- `!yedekle` - Sunucu ayarlarını yedekler
- `!profil [@kullanıcı]` - Kullanıcı profilini gösterir

## Premium Üyelik

Premium üyelik aylık 1.99$ karşılığında satın alınabilir. Premium üyelik ile:
- Gelişmiş moderasyon özellikleri
- Özelleştirilebilir komutlar
- Otomatik yedekleme
- Detaylı sunucu istatistikleri
- ve daha fazlası...

## Destek

Herhangi bir sorun veya öneriniz için GitHub üzerinden issue açabilirsiniz. 
