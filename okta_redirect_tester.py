import asyncio
from playwright.async_api import async_playwright

async def test_okta_redirection():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # ساخت مستقیم URL نهایی با هدایت به Okta و تزریق دامنه‌ی مخرب در redirect_uri
        malicious_redirect = "https://evil.com/"
        okta_target = f"https://monashuni.okta.com/oauth2/aus6nmxblRA2pQlap3l6/v1/authorize?client_id=0oa6nns1vMGFUL63s3l6&redirect_uri={malicious_redirect}&response_type=code&scope=openid%20profile%20email%20offline_access&state=d64c41cc37244611b5292137785262b9&code_challenge=6anXn-UqPlQzItxLtsA9R1m_fSohH76CbeKiEGvTnZE&code_challenge_method=S256&response_mode=query"

        print(f"[*] Testing direct navigation to Okta with injected redirect_uri...")
        
        try:
            response = await page.goto(okta_target, timeout=30000, wait_until="networkidle")
            print(f"[+] HTTP Status from Okta: {response.status if response else 'No response'}")
            print(f"[+] Final URL rendered by browser: {page.url}")

            # بررسی متن صفحه برای یافتن خطاهای رایج اعتبارسنجی Okta
            page_content = await page.content()
            if "invalid_redirect_uri" in page_content or "The redirect_uri parameter must" in page_content:
                print("[!] Server-side validation PASSED: Okta correctly rejected the unauthorized redirect_uri.")
            else:
                print("[+] Potential anomaly detected! Checking page text for clues...")
                # چاپ بخشی از متن صفحه برای تحلیل
                snippet = await page.evaluate("document.body.innerText.substring(0, 300)")
                print(f"    Page snippet: {snippet.strip()}")

            # ذخیره اسکرین‌شات برای بررسی دقیق بصری
            await page.screenshot(path="/root/recon/monash/okta_test_result.png")
            print("[+] Screenshot saved to /root/recon/monash/okta_test_result.png")

        except Exception as e:
            print(f"[!] Error during Okta redirect test: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_okta_redirection())
