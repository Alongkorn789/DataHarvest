import requests
from bs4 import BeautifulSoup
import time # สำหรับหน่วงเวลา
import random

id_category = 14
total_pages = 3  # ระบุจำนวนหน้าตามที่เห็นในเว็บ
total_count = 0  # ตัวนับจำนวนรายการทั้งหมด

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

print(f"--- เริ่มต้นการดึงข้อมูลทั้งหมด {total_pages} หน้า ---")

for page in range(1, total_pages + 1):
    # สร้าง URL ของแต่ละหน้า
    url = f"https://x-raybangkok.com/category.php?id_category={id_category}&p={page}"
    print(f"\nกำลังดึงหน้าที: {page} ...")
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            product_list = soup.find_all('li', class_='ajax_block_product')

            for item in product_list:
                total_count += 1 # เพิ่มจำนวนนับ
                
                link_tag = item.find('a', class_='product_img_link')
                name = link_tag.get('title') if link_tag else "ไม่มีชื่อสินค้า"
                
                price_tag = item.find('span', class_='price')
                price = price_tag.get_text(strip=True) if price_tag else "ไม่ระบุราคา"
                
                print(f"{total_count}. {name} | ราคา: {price}")

            # มารยาทบอท: หยุดพักสั้นๆ ก่อนไปหน้าถัดไป
            time.sleep(random.uniform(1, 2)) 
            
        else:
            print(f"หน้า {page} เข้าถึงไม่ได้ (Status: {response.status_code})")

    except Exception as e:
        print(f"เกิดข้อผิดพลาดที่หน้า {page}: {e}")

print(f"\nเสร็จสิ้น! ดึงข้อมูลมาได้ทั้งหมด {total_count} รายการ")