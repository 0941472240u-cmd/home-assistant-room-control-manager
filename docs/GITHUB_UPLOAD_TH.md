# การนำ Repository ขึ้น GitHub

1. แตกไฟล์ ZIP ลงในคอมพิวเตอร์
2. เปิด Terminal ในโฟลเดอร์ `home-assistant-room-control-manager`
3. ตั้งค่าเจ้าของ Repository ใน `manifest.json` ด้วยคำสั่ง:

   ```bash
   python scripts/set_github_owner.py ชื่อบัญชี_GitHub
   ```

4. สร้าง Public Repository บน GitHub ชื่อ `home-assistant-room-control-manager`
5. อัปโหลดด้วย Git:

   ```bash
   git init
   git add .
   git commit -m "Release 0.1.0"
   git branch -M main
   git remote add origin https://github.com/ชื่อบัญชี_GitHub/home-assistant-room-control-manager.git
   git push -u origin main
   ```

6. เปิดแท็บ **Actions** และรอให้ Tests, Hassfest และ HACS validation ทำงาน
7. เมื่อทุก Workflow ผ่าน ให้สร้าง Tag:

   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

8. Workflow `Publish release` จะสร้าง GitHub Release และแนบ Source Archive ให้อัตโนมัติ

หาก Workflow ใดไม่ผ่าน ห้ามถือว่า Release พร้อมใช้งาน ให้เปิดรายละเอียดของ Workflow และแก้ข้อผิดพลาดก่อนสร้าง Tag ใหม่
