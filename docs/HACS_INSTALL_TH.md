# การติดตั้งผ่าน HACS Custom Repository

1. ตรวจว่า Repository บน GitHub เป็น Public และมี Release `v0.1.0`
2. เปิด Home Assistant แล้วเข้า **HACS**
3. เข้า **Integrations**
4. กดเมนูสามจุดมุมขวาบน แล้วเลือก **Custom repositories**
5. วาง URL ของ GitHub Repository
6. เลือกประเภท **Integration** แล้วกด **Add**
7. เปิดรายการ **Room Control Manager** แล้วกด **Download**
8. Restart Home Assistant
9. ไปที่ **Settings → Devices & services → Add integration**
10. ค้นหา **Room Control Manager** และเริ่มเพิ่มห้อง

รุ่น 0.1.0 ทำงานแบบ Dry Run เท่านั้นและไม่มีโค้ดส่งคำสั่งจริงไปยังอุปกรณ์
