# Room Control Manager 0.1.0

Home Assistant Custom Integration สำหรับเลือกเซ็นเซอร์และอุปกรณ์ของแต่ละห้องผ่านหน้า UI โดยไม่ฝัง Entity ID ไว้ใน Source Code

## ความปลอดภัยของรุ่น 0.1.0

รุ่นนี้เป็น **Dry Run เท่านั้น** ระบบอ่านสถานะ ประเมินเงื่อนไข แสดงคำสั่งที่ตั้งใจ และบันทึก Log แต่ไม่มีโค้ดเรียก Service ของ `light`, `switch`, `fan`, `climate` หรือ `script`

Dry Run ถูกบังคับไว้ใน Runtime และ Options Flow ผู้ใช้ไม่สามารถเปลี่ยนรุ่น 0.1.0 ให้ส่งคำสั่งจริงได้

## ความสามารถ

- เพิ่ม Config Entry ได้หลายห้อง
- เลือก Door, Presence, Motion, Temperature, Illuminance, Light, Fan, Climate และ IR Scripts ผ่าน Entity Selector
- เปลี่ยนอุปกรณ์ผ่าน Reconfigure
- เปลี่ยน Threshold, Delay และวิธีรวม Sensor ผ่าน Configure/Options
- Sensor ใช้ร่วมกันได้พร้อมคำเตือน
- Actuator และ IR Script ห้ามซ้ำข้ามห้อง
- แยกสถานะความพร้อมเป็นรายโมดูล
- Entity หายหรือ unavailable จะปิดเฉพาะโมดูลที่เกี่ยวข้อง
- Diagnostics ปกปิดชื่อห้อง Area และ Entity ID
- สร้าง Repair Issue เมื่อ Entity หาย unavailable หรือโมดูลตั้งค่าไม่ครบ

## รุ่น Home Assistant ขั้นต่ำ

Home Assistant `2026.3.0` และ HACS `2.0.0` ขึ้นไป ค่ารุ่นขั้นต่ำอยู่ใน `hacs.json` ซึ่งเป็นตำแหน่งที่ HACS รองรับสำหรับการจำกัดรุ่น Home Assistant

## ตั้งค่า GitHub metadata ก่อนอัปโหลด

Repository ZIP ยังไม่ทราบชื่อบัญชี GitHub ของผู้ใช้ จึงมีสคริปต์สำหรับตั้ง URL และ Code Owner ให้ตรงกับ Repository จริง:

```bash
python scripts/set_github_owner.py ชื่อบัญชี_GitHub
```

สคริปต์จะแก้ `documentation`, `issue_tracker` และ `codeowners` ใน `manifest.json`

## ติดตั้งผ่าน HACS Custom Repository

1. นำ Repository นี้ขึ้น GitHub แบบ Public และสร้าง GitHub Release ชื่อ `v0.1.0`
2. เปิด HACS → Integrations
3. เปิดเมนูสามจุด → Custom repositories
4. วาง URL ของ Repository และเลือกประเภท **Integration**
5. กด Add จากนั้นเปิด Repository และกด Download
6. Restart Home Assistant
7. ไปที่ Settings → Devices & services → Add integration
8. ค้นหา **Room Control Manager**

รายละเอียดเพิ่มเติมอยู่ใน `docs/GITHUB_UPLOAD_TH.md` และ `docs/HACS_INSTALL_TH.md`

## ตั้งค่าห้อง

Config Flow จะถามชื่อห้อง เซ็นเซอร์ อุปกรณ์ และวิธีควบคุมแอร์ เมื่อบันทึกแล้วระบบเริ่ม Dry Run ทันที

- เปลี่ยนอุปกรณ์: Settings → Devices & services → Room Control Manager → เมนู Config Entry → Reconfigure
- เปลี่ยนพฤติกรรม: Settings → Devices & services → Room Control Manager → Configure

## ตรวจผล Dry Run

ดู Entity ที่ Integration สร้าง:

- Configuration status
- Dry Run
- Last intended action
- Last decision reason
- Ready modules
- Problem modules
- Effective occupancy

เปิด Log ที่ Settings → System → Logs และค้นหา `room_control_manager`

แผนทดสอบโดยละเอียดอยู่ใน `docs/DRY_RUN_TEST_PLAN_TH.md`

## Translation

มี `strings.json` เป็นข้อความต้นฉบับของโครงการ และมี `translations/en.json` กับ `translations/th.json` สำหรับการแสดงผลของ Custom Integration
