# Subnet Ping Monitor

Bu proje, girilen bir IP/Subnet bloğu içindeki IP adreslerine ping atarak sonuçları loglayan, cache’leyen ve veritabanında saklayan bir sistemdir. Django REST Framework, Celery, Redis ve PostgreSQL kullanılarak geliştirilmiştir.

## Özellikler

- Kullanıcıdan IP/Subnet bilgisi alır.
- Subnet mask'ı kontrol eder (IPv4 için maksimum /24, IPv6 için /64).
- Ping sonuçlarını veritabanına yazar.
- Her IP için:
  - Ulaşılıp ulaşılamadığı
  - Gecikme süresi (ms)
  - Kontrol zamanı bilgilerini kaydeder.
- Celery ile görev kuyruğa alınır, Redis ile yönetilir.
- Sonuçlar aynı zamanda Redis cache’e yazılır (saatlik).
- Docker ile ayağa kaldırılabilir.

## Kullanılan Teknolojiler

- Python
- Django & Django REST Framework
- Celery
- Redis
- PostgreSQL
- Docker & docker-compose
- ping3 (ping atmak için)

## Kurulum

### 1. Depoyu Klonla

```bash
git clone https://github.com/kullaniciadi/subnet-ping-monitor.git
cd subnet-ping-monitor
```

### 2. Ortam Değişkenlerini Ayarla

`.env` dosyası oluştur ve gerekli ayarları yap:

```
SECRET_KEY=your_secret_key
DEBUG=True
POSTGRES_DB=pingdb
POSTGRES_USER=pinguser
POSTGRES_PASSWORD=pingpass
```

### 3. Docker ile Başlat

```bash
docker-compose up --build
```

Ardından veritabanı için migration işlemlerini çalıştır:

```bash
docker-compose exec web python manage.py migrate
```

### 4. Celery Worker Başlat

```bash
docker-compose exec web celery -A pingmonitor worker -l info --pool=solo
```

## API Kullanımı

### Subnet Tarama Başlat (POST)

```http
POST /api/subnet-scan/

Body:
{
  "ip_network": "192.168.1.0/24"
}
```

Başarılı olursa: `201 Created`

### Ping Sonuçlarını Görüntüle (GET)

```http
GET /api/subnet-scan/{subnet_id}/results/
```

## Teknik Bilgiler

### Akış Diyagramı

1. Kullanıcı Subnet gönderir.
2. IP listesi üretilir.
3. Her IP için Celery görevi oluşturulur.
4. `ping3` ile ping atılır.
5. Sonuç hem veritabanına hem Redis’e yazılır.

### Topoloji

```
Kullanıcı → Django API → Celery Görevi → ping3 → PostgreSQL + Redis
```

## Uyarılar

- `192.168.0.0/16` gibi büyük subnet’ler çok sayıda görev oluşturur. Geliştirme ve test için küçük subnet kullanın (`/30`, `/29` gibi).
- Windows ortamında Celery çalıştırırken `--pool=solo` kullanmanız gerekir.
- Redis’e düşen görevler durmaz, veritabanındaki veriler silinse bile yeniden çalıştırılınca kalan görevler çalışabilir. Redis kuyruklarını temizlemek için:

```bash
docker-compose exec redis redis-cli FLUSHALL
```

## Örnek Redis Cache Key

```
ping_result:{subnet_request_id}:{ip}
```

Örnek içerik:

```json
{
  "ip_address": "192.168.1.10",
  "is_alive": true,
  "response_time_ms": 3.22,
  "checked_at": "2025-07-08T14:52:00"
}
```

---

Hazırlayan: Kutay Yıldırım  
Proje: Subnet Ping Monitor