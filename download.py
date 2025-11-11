import os
import json
import concurrent.futures
from playwright.sync_api import sync_playwright

def save_with_playwright(kid):
    # print(kid)
    # 跳过已经完成下载的文件
    if os.path.exists("codb_data",kid+"_data.txt"):
        return
    url = "http://www.cyanoomics.cn/lz/cyano_detail/"+kid
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        finish_flag = True
        try:
            page.goto(url, wait_until='domcontentloaded')
            page.wait_for_timeout(3000)
            
            # Xpath解析
            gid = page.query_selector('xpath=//body/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[3]/div[2]')
            pid = page.query_selector('xpath=//body/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[3]/div[1]/div[6]/div[5]')
            go_id = page.query_selector('xpath=//body/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[3]/div[1]/div[4]/div[5]')
            
            with open(os.path.join("codb_data",kid+"_data.txt"),'w') as f:
                if gid:
                    f.write(gid.text_content()+'\n')
                else:
                    f.write('.\n')
                    finish_flag = False
                if pid:
                    f.write(pid.text_content()+'\n')
                else:
                    f.write('.\n')
                    finish_flag = False
                if go_id:
                    f.write(go_id.text_content()+'\n')
                else:
                    f.write('.\n')
                    finish_flag = False
            
        except Exception as e:
            print(f"error: {e}")
            finish_flag = False
        finally:
            browser.close()
        if not finish_flag:
            print(kid,"query failed")

with open("kegg_id.json",'r') as f:
    kegg_id = json.load(f)

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    executor.map(save_with_playwright, kegg_id)