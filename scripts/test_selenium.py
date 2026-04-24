from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import random

# --- 1. ตั้งค่า Selenium ---
chrome_options = Options()
# chrome_options.add_argument("--headless")  # เปิดบรรทัดนี้ถ้าไม่อยากให้หน้าต่าง Browser เด้งขึ้นมา
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

id_category = 14
total_pages = 3
total_count = 0

try:
    print(f"--- เริ่มต้นการดึงข้อมูลด้วย Selenium ทั้งหมด {total_pages} หน้า ---")

    for page in range(1, total_pages + 1):
        url = f"https://x-raybangkok.com/category.php?id_category={id_category}&p={page}"
        print(f"\nกำลังดึงหน้าที: {page} ...")
        
        # 2. สั่งให้ Browser เปิด URL
        driver.get(url)
        
        # 3. หน่วงเวลาเล็กน้อยเพื่อให้หน้าเว็บโหลดเสร็จ (Selenium ไม่รอให้เว็บโหลดจบเองเหมือน Requests)
        time.sleep(2) 

        # 4. ค้นหาไอเทมสินค้าทั้งหมด
        # ใช้ By.CSS_SELECTOR หรือ By.CLASS_NAME ก็ได้ครับ
        product_list = driver.find_elements(By.CLASS_NAME, 'ajax_block_product')

        for item in product_list:
            total_count += 1
            
            try:
                # 5. ดึงชื่อและลิงก์
                # หมายเหตุ: Selenium จะหา element ภายใน element ได้เหมือน BS4
                link_tag = item.find_element(By.CLASS_NAME, 'product_img_link')
                name = link_tag.get_attribute('title')
                link = link_tag.get_attribute('href')
                
                # 6. ดึงราคา
                price_tag = item.find_element(By.CLASS_NAME, 'price')
                price = price_tag.text
                
                print(f"{total_count}. {name} | ราคา: {price}")
                
            except Exception:
                print(f"{total_count}. [Error] ดึงข้อมูลสินค้าบางส่วนไม่ได้")

        # พักสายตาบอท
        time.sleep(random.uniform(1, 2))

finally:
    # 7. สำคัญมาก: ต้องปิด Browser เมื่อทำงานเสร็จ ไม่เช่นนั้น RAM จะเต็มครับ
    print(f"\nเสร็จสิ้น! รวมทั้งหมด {total_count} รายการ")
    driver.quit()