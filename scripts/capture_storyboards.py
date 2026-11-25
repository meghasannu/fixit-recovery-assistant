"""Capture the storyboard frames by driving the running app in a browser.

Walks through the three storyboard scenarios and saves each frame, cropped to
the relevant part of the page, to docs/storyboards/frames/. Run it against the
live model to capture real Gemini answers (they differ from run to run).

Setup (once):     pip install playwright
Run the app:      uvicorn app.main:app
Then, in a second terminal:
                  python -m scripts.capture_storyboards
Options:          --url http://localhost:8000   --browser msedge|chrome
"""

import argparse
import asyncio
from pathlib import Path

OUT = Path("docs/storyboards/frames")
CALL_TIMEOUT = 90_000  # ms; live model calls can be slow when busy


async def shot(page, name: str, selectors: list[str], pad: int = 12):
    """Screenshot the area covering all visible elements in `selectors`."""
    sels = []
    for sel in selectors:
        loc = page.locator(sel).first
        if await loc.count() and await loc.is_visible():
            sels.append(sel)
    if not sels:
        raise RuntimeError(f"{name}: none of {selectors} is visible")
    # Measure every element in page coordinates in one go, so scrolling
    # between measurements cannot shift the crop.
    clip = await page.evaluate(
        """([sels, pad]) => {
          const r = sels.map(s => document.querySelector(s).getBoundingClientRect());
          const x0 = Math.max(0, Math.min(...r.map(e => e.left)) - pad + scrollX);
          const y0 = Math.max(0, Math.min(...r.map(e => e.top)) - pad + scrollY);
          const x1 = Math.max(...r.map(e => e.right)) + pad + scrollX;
          const y1 = Math.max(...r.map(e => e.bottom)) + pad + scrollY;
          return {x: x0, y: y0, width: x1 - x0, height: y1 - y0};
        }""", [sels, pad])
    await page.screenshot(path=str(OUT / f"{name}.png"), full_page=True, clip=clip)
    print(f"saved {name}.png")


async def versions(page, n: int):
    await page.wait_for_function(
        f"document.querySelectorAll('#history-list li').length >= {n}",
        timeout=CALL_TIMEOUT)
    await page.mouse.move(0, 0)
    await page.wait_for_timeout(300)


async def fresh(page, url: str, sample: str):
    await page.goto(url)
    await page.wait_for_selector("#sample-select option[value='too-technical']", state="attached")
    await page.select_option("#sample-select", sample)


async def storyboard_1(page, url):
    await fresh(page, url, "too-technical")
    await shot(page, "s1-1", ["label[for=request]", "#request", "#generate-btn"])
    await page.click("#generate-btn")
    await versions(page, 1)
    await shot(page, "s1-2", ["#output", "#output-meta"])
    # Keyboard focus shows the same hint as hovering and keeps it on screen.
    await page.focus("[data-control=simpler]")
    await page.wait_for_timeout(300)
    await shot(page, "s1-3", ["#noticed", "#fix-buttons", "#fix-hint"])
    await page.click("[data-control=simpler]")
    await versions(page, 2)
    await shot(page, "s1-4", ["#version-bar", "#output", "#change-report", "#output-meta"])
    await shot(page, "s1-5", ["#history-heading", "#history-list"])


async def storyboard_2(page, url):
    await fresh(page, url, "missing-point")
    await page.click("#generate-btn")
    await versions(page, 1)
    await shot(page, "s2-1", ["#output", "#noticed"])
    await page.click("#autofix-btn")
    await page.wait_for_selector("#proposal:not([hidden])", timeout=CALL_TIMEOUT)
    await page.wait_for_timeout(300)
    await shot(page, "s2-2", ["#proposal"])
    await page.click("#proposal-edit")
    text = await page.input_value("#proposal-text")
    await page.fill("#proposal-text", text.rstrip(".") + ". Keep it to about 80 words.")
    await shot(page, "s2-3", ["#proposal"])
    await page.click("#proposal-run")
    await versions(page, 2)
    await shot(page, "s2-4", ["#version-bar", "#output", "#change-report", "#output-meta"])
    await page.click("#accept-btn")
    await page.wait_for_selector("#summary:not([hidden])")
    await page.mouse.move(0, 0)
    await page.wait_for_timeout(400)
    await shot(page, "s2-5", ["#accept-row", "#summary"])


async def storyboard_3(page, url):
    await fresh(page, url, "too-technical")
    await page.click("#generate-btn")
    await versions(page, 1)
    await page.click("[data-control=shorter]")
    await versions(page, 2)
    await shot(page, "s3-1", ["#version-bar", "#output", "#change-report", "#output-meta", "#noticed"])
    await page.click("#undo-btn")
    await page.wait_for_timeout(200)
    await shot(page, "s3-2", ["#status", "#version-bar", "#output", "#output-meta"])
    await page.fill("#correction", "Use plain words and mention that plants release oxygen")
    await page.click("#correct-btn")
    await versions(page, 3)
    await shot(page, "s3-3", ["#version-bar", "#output", "#change-report", "#output-meta"])
    await page.fill("#correction", "Add the name of the scientist who discovered this")
    await page.click("#correct-btn")
    await versions(page, 4)
    await shot(page, "s3-4", ["#version-bar", "#output"])
    await shot(page, "s3-5", ["#history-heading", "#history-list"])


async def main(url: str, browser: str, executable: str | None):
    from playwright.async_api import async_playwright

    OUT.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        if executable:
            b = await p.chromium.launch(executable_path=executable)
        else:
            b = await p.chromium.launch(channel=browser)
        page = await b.new_page(viewport={"width": 1300, "height": 1000},
                                device_scale_factor=2)
        for run in (storyboard_1, storyboard_2, storyboard_3):
            await run(page, url)
        await b.close()
    print(f"\nAll frames saved in {OUT}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Capture storyboard frames.")
    ap.add_argument("--url", default="http://localhost:8000")
    ap.add_argument("--browser", default="msedge", help="installed browser: msedge or chrome")
    ap.add_argument("--executable", default=None, help="path to a browser executable")
    args = ap.parse_args()
    asyncio.run(main(args.url, args.browser, args.executable))
