import os
from playwright.sync_api import sync_playwright
from PIL import Image

html_path = r"C:\Users\choud\.gemini\antigravity\scratch\ai-business-dashboard\PRESENTATION.html"
file_uri  = "file:///" + html_path.replace("\\", "/")
output_dir = os.path.dirname(html_path)
pdf_path  = os.path.join(output_dir, "ai_business_dashboard_presentation.pdf")

def generate_pdf():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=2   # 2x retina -> 3840x2160
        )
        page = context.new_page()
        print(f"Loading {file_uri}")
        page.goto(file_uri)
        page.wait_for_timeout(3000)

        # Check number of slides
        total_slides = page.evaluate("document.querySelectorAll('.slide').length")
        print(f"Detected {total_slides} slides.")

        screenshots = []
        for i in range(total_slides):
            print(f"Capturing slide {i+1}/{total_slides}...")
            page.evaluate(f"goToSlide({i})")
            page.wait_for_timeout(1000)
            path = os.path.join(output_dir, f"_tmp_dashboard_slide_{i}.png")
            page.screenshot(path=path, full_page=False)
            screenshots.append(path)

        browser.close()

    print("Combining slides into high-resolution PDF...")
    if screenshots:
        images = [Image.open(p).convert("RGB") for p in screenshots]
        images[0].save(pdf_path, save_all=True, append_images=images[1:], resolution=200.0)
        for p in screenshots:
            try: os.remove(p)
            except: pass
        print(f"[OK] Generated: {pdf_path}")
        print(f"     Resolution: {images[0].size[0]}x{images[0].size[1]} px/slide | 200 DPI")

if __name__ == "__main__":
    generate_pdf()
