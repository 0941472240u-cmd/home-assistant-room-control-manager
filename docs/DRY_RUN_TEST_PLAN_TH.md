# แผนทดสอบ Dry Run รุ่น 0.1.0

## 1. เตรียมระบบ

- สำรองข้อมูล Home Assistant
- คง Automation เดิมไว้ใน Manual หรือปิด Automation ที่อาจรบกวนการสังเกตผล
- ติดตั้ง Integration และ Restart Home Assistant

## 2. เพิ่มห้อง

- เพิ่ม Room Control Manager จากหน้า Devices & services
- ตั้งชื่อห้อง
- เลือกเฉพาะ Entity ที่ต้องการทดสอบ
- ยืนยันว่าหน้าสรุประบุ `Dry Run`

## 3. ตรวจ Entity สถานะ

ตรวจว่ามี Entity ต่อไปนี้:

- Configuration status
- Dry Run
- Last intended action
- Last decision reason
- Ready modules
- Problem modules
- Effective occupancy

ค่า Dry Run ต้องเป็น `on` ตลอดเวลา

## 4. ทดสอบ Presence และ Motion

- ทำให้เซ็นเซอร์เปลี่ยนเป็นพบคน
- ตรวจ Effective occupancy
- ทำให้ไม่พบคนและรอตามเวลาหน่วง
- ตรวจเหตุผลล่าสุดและ Intended action

## 5. ทดสอบแสง

- ทำให้ค่าแสงต่ำกว่าเกณฑ์เปิดไฟ
- ตรวจว่าระบบรายงานความตั้งใจเปิดไฟ แต่ไฟจริงต้องไม่เปลี่ยนสถานะ
- ทำให้ค่าแสงสูงกว่าเกณฑ์ปิดไฟ
- ตรวจว่าระบบรายงานความตั้งใจปิดไฟ โดยไม่มี Service Call จริง

## 6. ทดสอบอุณหภูมิ

- ทำให้อุณหภูมิสูงกว่าเกณฑ์เปิดพัดลมหรือแอร์
- ตรวจ Intended action และ Reason
- ทำให้อุณหภูมิต่ำกว่าเกณฑ์ปิด
- ยืนยันว่าพัดลมและแอร์จริงไม่ถูกสั่ง

## 7. ทดสอบ Entity unavailable

- ทำให้ Sensor หรือ Actuator หนึ่งตัวเป็น unavailable
- ตรวจว่าเฉพาะโมดูลที่พึ่งพา Entity นั้นเข้าสู่ Problem
- ตรวจ Repair Issue และ System Log
- ตรวจว่าโมดูลอื่นยังประเมินต่อได้

## 8. ทดสอบหลายห้องและ Ownership

- เพิ่มห้องที่สองโดยใช้ Sensor ร่วมกัน ต้องมีคำเตือนแต่บันทึกได้
- ลองเลือก Light, Fan, Climate หรือ IR Script ที่ห้องแรกใช้แล้ว ต้องถูกปฏิเสธ

## 9. ตรวจ Diagnostics

- ดาวน์โหลด Diagnostics จากหน้า Integration
- ตรวจว่าชื่อห้อง Area และ Entity ID ถูกปกปิดหรือแปลงเป็น Token

## 10. เกณฑ์ผ่าน

- ไม่มีอุปกรณ์จริงเปลี่ยนสถานะจาก Integration
- Intended action และ Reason เปลี่ยนตามข้อมูลเซ็นเซอร์
- ไม่มี Service Call ของ light, switch, fan, climate หรือ script
- Entity unavailable กระทบเฉพาะโมดูลที่เกี่ยวข้อง
- Repair Issue ถูกสร้างเมื่อมีปัญหาและหายเมื่อแก้ไขแล้ว
