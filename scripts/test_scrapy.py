import scrapy
from scrapy.crawler import CrawlerProcess

class XraySpider(scrapy.Spider):
    name = 'xray_spider'

     # 1. ตั้งค่าการทำงาน (เหมือนการตั้ง Headers และ Delay ในโค้ดเดิม)
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'DOWNLOAD_DELAY': 1.5,      # หน่วงเวลา 1.5 วินาทีอัตโนมัติ
        'RANDOMIZE_DOWNLOAD_DELAY': True, # สุ่มช่วงเวลาหน่วงเพื่อให้เหมือนคน
        'LOG_LEVEL': 'INFO',         # แสดงเฉพาะข้อมูลที่สำคัญ

        
        # ส่วนที่เพิ่มเข้ามาสำหรับการบันทึกไฟล์
        'FEEDS': {
            'products.csv': { # ชื่อไฟล์ที่ต้องการ
                'format': 'csv',
                'encoding': 'utf-8-sig',
                'overwrite': True, # ให้เขียนทับไฟล์เดิมทุกครั้งที่รัน
            },
        },


    }

    # 2. ฟังก์ชันเริ่มต้นส่งคำขอ (Request)
    def start_requests(self):
        id_category = 14
        total_pages = 3
        for page in range(1, total_pages + 1):
            url = f"https://x-raybangkok.com/category.php?id_category={id_category}&p={page}"
            yield scrapy.Request(url=url, callback=self.parse)

    # 3. ฟังก์ชันแกะข้อมูล (เหมือน BeautifulSoup)
    def parse(self, response):
        # Scrapy ใช้ CSS Selector ซึ่งเขียนสั้นกว่า BS4 มากครับ
        # .ajax_block_product คือ class ของ <li>
        products = response.css('li.ajax_block_product')

        for product in products:
            # ดึงข้อมูลชื่อจาก attribute 'title'
            name = product.css('a.product_img_link::attr(title)').get()
            # ดึงราคาจากข้อความใน span.price
            raw_price = product.css('span.price::text').get()


            if raw_price:
                # 1. ลบ ฿ และ , ออก
                clean_price = raw_price.replace('฿', '').replace(',', '').strip()
    
                # 2. พยายามแปลงเป็นตัวเลข (ถ้าเป็น "0" ก็จะได้ 0)
                try:
                    final_price = int(clean_price)
                except:
                    final_price = 0 # หรือจัดการกรณีที่เป็นข้อความอื่น
            else:
                final_price = 0



            # ดึงลิงก์
            link = product.css('a.product_img_link::attr(href)').get()

            # ส่งค่าออกมาเป็น Dictionary (Scrapy จะจัดการเก็บลงไฟล์ให้เราเอง)
            yield {
                'name': name.strip() if name else "N/A",
                'price': final_price if final_price > 0 else None, # ใช้ None แทนข้อความ
                'link': link
            }

# --- ส่วนการรันโปรแกรม ---
if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(XraySpider)
    process.start()