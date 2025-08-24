# Coolify Deployment Guide

Bu döküman Turkish Legal AI API'sini Coolify ile VPS'nizde nasıl deploy edeceğinizi açıklar.

## 1. Ön Hazırlıklar

### Gereksinimler
- Coolify kurulu VPS
- Docker ve Docker Compose desteği
- OpenRouter API Key

## 2. Coolify'da Yeni Proje Oluşturma

1. Coolify dashboard'a girin
2. **New Project** > **Git Repository** seçin
3. Repository URL'sini girin
4. Branch olarak `main` seçin

## 3. Environment Variables Ayarlama

Coolify'da Environment sekmesinde şu değişkenleri ekleyin:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
PORT=8001
HOST=0.0.0.0
PYTHONPATH=/app
```

## 4. Docker Konfigürasyonu

Coolify otomatik olarak `docker-compose.yml` dosyasını algılar ve kullanır.

### Port Konfigürasyonu
- Internal Port: 8001
- External Port: 8001 (veya istediğiniz port)

## 5. Domain ve SSL

1. **Domains** sekmesinde domain ekleyin
2. Let's Encrypt SSL sertifikası otomatik olarak yapılandırılır
3. Örnek: `yargi-api.yourdomain.com`

## 6. Deploy İşlemi

1. **Deploy** butonuna basın
2. Build logs'u takip edin
3. Deploy tamamlandıktan sonra health check'i bekleyin

## 7. Test

Deploy tamamlandıktan sonra:

```bash
# Health check
curl https://yargi-api.yourdomain.com/health

# API docs
curl https://yargi-api.yourdomain.com/docs
```

## 8. Monitoring

Coolify dashboard'da:
- Resource usage (CPU, RAM)
- Application logs
- Build logs
- Health check status

## 9. Güncelleme

Git repository'de değişiklik yaptığınızda:
1. Coolify otomatik olarak webhook'ları algılar
2. Auto-deploy aktifse otomatik güncellenir
3. Manuel deploy için **Deploy** butonunu kullanın

## 10. Backup

Coolify otomatik olarak backup'lar alır:
- Database backups (yoksa gerek yok)
- Application files
- Configuration

## 11. Troubleshooting

### Build hatası
- Build logs'u kontrol edin
- Requirements.txt eksik paketler olabilir

### Health check başarısız
- Port 8001'in açık olduğundan emin olun
- Container logs'u kontrol edin

### API çalışmıyor
- OPENROUTER_API_KEY'in doğru olduğundan emin olun
- Environment variables'ı kontrol edin

## 12. Avantajlar

✅ **Kendi VPS'iniz** - tam kontrol
✅ **SSL otomatik** - Let's Encrypt entegrasyonu  
✅ **Monitoring dahil** - resource tracking
✅ **Auto-deploy** - git webhook desteği
✅ **Backup otomatik** - veri güvenliği
✅ **Domain yönetimi** - kolay subdomain

Bu şekilde Railway'den çok daha fazla kontrolünüz olacak ve maliyeti de daha düşük olur.