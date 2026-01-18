# 🤖 Telegram Bot Admin Panel

Bu loyiha **Telegram bot** uchun yozilgan **admin panel tizimi** bo‘lib, unda:
- 👑 **Super admin**
- 🛡 **Oddiy admin**
rollari mavjud.

Bot orqali adminlar va stars paketlar boshqariladi.

---

## 🔐 Rollar va Huquqlar

### 👑 Super Admin
Super admin — eng yuqori huquqlarga ega foydalanuvchi.

Quyidagi amallarni bajara oladi:
- ➕ Admin qo‘shish
- ➖ Admin o‘chirish
- ⭐ Stars paketlar narxini **o‘zgartirish**
- 👀 Stars paketlarni ko‘rish
- 👥 Foydalanuvchilarni ko‘rish

Super admin ID `config` faylda belgilanadi.

```python
SUPERADMIN_ID = 123456789
