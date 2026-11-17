import os
import sys
from playwright.sync_api import sync_playwright
d,prefix=sys.argv[1],sys.argv[2]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":1080,"height":1350})
    pg.goto(f"file://{d}/cards.html"); pg.wait_for_timeout(500)
    for i,el in enumerate(pg.query_selector_all(".slide"),1):
        el.screenshot(path=os.path.join(os.environ.get("OUT_DIR","/mnt/user-data/outputs"),f"{prefix}_{i}.png"))
    b.close()
print("ok")
