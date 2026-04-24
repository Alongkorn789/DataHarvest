# DataHarvest
DataHarvest เป็นโปรเจกต์ที่รวบรวมเทคนิคการดึงข้อมูลจากเว็บไซต์ (Web Scraping & Crawling) หลากหลายรูปแบบ โดยเน้นการดึงข้อมูลอย่างเป็นระบบ ถูกต้องตามหลักจริยธรรม และรองรับทั้งหน้าเว็บแบบ Static และ Dynamic

## โครงสร้างโปรเจกต์ (Project Structure)
```text
DataHarvest/
├── data/                      # โฟลเดอร์เก็บข้อมูลผลลัพธ์ (CSV, XLSX)
│   └── .gitkeep               # ไฟล์รักษาโครงสร้างโฟลเดอร์บน Git
├── scripts/                   # รวม Source Code ของการดึงข้อมูล
│   ├── allow_robot.py         # ตรวจเช็ค robots.txt และตั้งค่าความสุภาพ
│   ├── test_BeautifulSoup.py  # การดึงข้อมูลพื้นฐานด้วย BeautifulSoup4
│   ├── test_selenium.py       # การดึงข้อมูล Dynamic Web (JS) ด้วย Selenium
│   └── test_scrapy.py         # ระบบรัน Spider ด้วย Scrapy Framework
├── venv/                      # [Ignored] สภาพแวดล้อมจำลอง Python
├── .gitignore                 # กำหนดไฟล์ที่ไม่ต้องนำขึ้น GitHub
├── README.md                  # คำอธิบายโปรเจกต์ (ไฟล์นี้)
└── requirements.txt           # รายการ Library ทั้งหมดที่ต้องติดตั้ง
```

## การติดตั้ง (Installation) Clone โปรเจกต์ไปยังเครื่องของคุณ:

git clone https://github.com/Alongkorn789/DataHarvest.git

cd DataHarvest

## สร้างและเปิดใช้งาน Virtual Environment:
py -3.11 -m venv venv

venv\Scripts\activate

## ติดตั้ง Library ทั้งหมด:
pip install -r requirements.txt

## วิธีการใช้งาน (Usage) คุณสามารถเลือกใช้เครื่องมือที่เหมาะสมกับเว็บไซต์เป้าหมายได้ ดังนี้:

1. ตรวจสอบสิทธิ์การเข้าถึง (Polite Crawler) 
ใช้สำหรับเช็คว่าเว็บไซต์อนุญาตให้ Bot เข้าถึงส่วนไหนได้บ้างผ่าน robots.txt

   python scripts/allow_robot.py

2. ดึงข้อมูลเว็บทั่วไป (Static Content)
ใช้ BeautifulSoup4 เหมาะสำหรับหน้าเว็บที่โหลดข้อมูลมาพร้อมกับ HTML

   python scripts/test_BeautifulSoup.py

3. ดึงข้อมูลเว็บที่ใช้ JavaScript (Dynamic Content)
ใช้ Selenium เพื่อจำลองการเปิด Browser (Chrome) เหมาะกับเว็บที่ต้องมีการเลื่อนหน้าจอหรือรอโหลดข้อมูล

   python scripts/test_selenium.py

4. การดึงข้อมูลความเร็วสูง (Scrapy Framework)
ใช้ Scrapy สำหรับโปรเจกต์ขนาดใหญ่ที่ต้องการประสิทธิภาพสูง

   python scripts/test_scrapy.py

## นโยบายความปลอดภัยและมารยาท (Ethics & Disclaimer)
Robots.txt: สคริปต์ในโปรเจกต์นี้ได้รับการออกแบบให้ตรวจสอบสิทธิ์การเข้าถึงก่อนเริ่มทำงานเสมอ

Rate Limiting: มีการตั้งค่า DOWNLOAD_DELAY เพื่อไม่ให้เป็นการโจมตี Server เป้าหมาย (DDOS)

Purpose: โปรเจกต์นี้สร้างขึ้นเพื่อวัตถุประสงค์ทางการศึกษาและการวิจัยข้อมูลเท่านั้น