import asyncio
from playwright.async_api import async_playwright

async def trace_network():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # رصد تمام درخواست‌های شبکه
        page.on("request", lambda req: print(f"[HTTP Request] {req.method} -> {req.url}"))
        
        # رصد پاسخ‌ها و کدهای وضعیت (مثل 301, 302, 403)
        page.on("response", lambda res: print(f"[HTTP Response] {res.status} <- {res.url}" if res.status >= 300 else None))

        # رصد تغییرات آدرس (Redirects)
        page.on("framenavigated", lambda frame: print(f"[Navigation] Frame navigated to: {frame.url}") if frame == page.main_frame else None)

        target_url = "https://identity.monash.edu/password?redirect_uri=https://evil.com/"
        print(f"[*] Tracing navigation to: {target_url}\n")

        try:
            await page.goto(target_url, timeout=30000, wait_until="networkidle")
        except Exception as e:
            print(f"[!] Navigation error or timeout: {e}")

        print(f"\n[+] Final landing URL: {page.url}")
        
        # بررسی نهایی sessionStorage پس از اتمام ریدایرکت‌ها
        final_storage = await page.evaluate("() => Object.fromEntries(Object.entries(sessionStorage))")
        print(f"[+] Final sessionStorage state: {final_storage}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(trace_network())
