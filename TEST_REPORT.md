# Test Report — Room Control Manager 0.1.0

วันที่ตรวจ: 2026-06-22

## สภาพแวดล้อมที่ใช้ตรวจในเครื่องมือสร้างไฟล์

- Python 3.13.5
- Home Assistant package 2026.2.3 แบบสภาพแวดล้อมทดสอบบางส่วน
- Pytest
- Ruff

## ผลที่รันจริง

| รายการ | ผล |
|---|---|
| `ruff check .` | ผ่าน |
| `python -m compileall -q custom_components scripts tests` | ผ่าน |
| `python scripts/validate_repository.py` | ผ่าน |
| `python scripts/check_release_version.py v0.1.0` | ผ่าน |
| `pytest -q` | ผ่าน 18 tests |
| ตรวจ JSON ทุกไฟล์ | ผ่าน |
| ตรวจ YAML ของ GitHub Workflows ด้วย PyYAML | ผ่าน |
| ทดสอบสร้าง Schema ทุกหน้า Config/Options | ผ่าน |
| Static scan ป้องกัน Home Assistant Service Call | ผ่าน |
| Scan ป้องกัน Entity ID ส่วนตัวที่ทราบ | ผ่าน |

## สิ่งที่ Tests ครอบคลุม

- Domain, version, `config_flow` และการไม่มี `single_config_entry`
- Repository มี Custom Integration เพียงตัวเดียว
- Dry Run ไม่มี Service Call ของ light, switch, fan, climate หรือ script
- ไม่มี Entity ID จริงที่ผู้ใช้เคยส่งอยู่ใน Repository
- Config Flow และ Options ใช้แนวทาง Reload เดียว
- Selector Schemas สร้างได้ทุกหน้า
- ค่า Default เปิดเฉพาะโมดูลที่มีอุปกรณ์ตั้งค่าไว้
- Sensor sharing และ Actuator ownership conflict
- Module isolation เมื่อ Entity unavailable
- Dry-run evaluator รายงาน intended actions ได้โดยไม่มี `services` object
- Diagnostics ปกปิดชื่อห้อง Area และ Entity ID

## สิ่งที่ยังไม่ได้รัน

- ยังไม่ได้เปิด Home Assistant instance เต็มระบบเพื่อกด Config Flow ผ่าน Frontend จริง
- ยังไม่ได้รัน HACS Action และ Hassfest บน GitHub เพราะ Repository ยังไม่ได้ถูก Push ขึ้น GitHub
- ยังไม่ได้รันชุดทดสอบบน Home Assistant 2026.3.0 หรือ 2026.6.4 ในเครื่องมือนี้ เนื่องจากทั้งสองรุ่นต้องใช้ Python 3.14.2 แต่สภาพแวดล้อมปัจจุบันเป็น Python 3.13.5
- การติดตั้ง dependency เต็มชุดของ Home Assistant ในสภาพแวดล้อมนี้หมดเวลาก่อนเสร็จ จึงไม่ได้ใช้ผล import เต็มระบบเป็นหลักฐาน

GitHub Workflow `tests.yml` ถูกกำหนดให้ทดสอบ Home Assistant 2026.3.0 และ 2026.6.4 บน Python 3.14 หลังจาก Push Repository แล้ว ผลของ Workflow เหล่านั้นต้องผ่านก่อนถือว่า Release พร้อมใช้งานจริง
