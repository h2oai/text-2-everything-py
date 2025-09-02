#!/usr/bin/env python3
import os
import subprocess
import sys
import shutil
import yaml
from pypdf import PdfReader, PdfWriter


def run(cmd: list[str]) -> None:
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if res.returncode != 0:
        print(res.stdout)
        raise SystemExit(res.returncode)


def ensure_chrome() -> str:
    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        shutil.which("google-chrome") or "",
        shutil.which("chromium") or "",
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return ""


def build_site() -> None:
    print("Building docs site...")
    run([sys.executable, "-m", "mkdocs", "build"])  # respects venv


def list_pages() -> list[str]:
    with open("mkdocs.yml", "r") as f:
        cfg = yaml.safe_load(f)
    nav = cfg.get("nav", [])
    paths: list[str] = []

    def add_page(path: str) -> None:
        if path.endswith(".md"):
            parts = path.split("/")
            if len(parts) == 1:
                # index.md -> index.html; other.md -> other/index.html
                if parts[0] == "index.md":
                    filename = "index.html"
                else:
                    filename = f"{parts[0].split('.')[0]}/index.html"
            else:
                # guides/chat.md -> guides/chat/index.html
                filename = "/".join(parts[:-1] + [parts[-1].split(".")[0], "index.html"])
            paths.append(filename)

    for item in nav:
        if isinstance(item, dict):
            for _, value in item.items():
                if isinstance(value, str):
                    add_page(value)
                elif isinstance(value, list):
                    for sub in value:
                        if isinstance(sub, dict):
                            for __, spath in sub.items():
                                if isinstance(spath, str):
                                    add_page(spath)
    return paths


def export_pdfs_chrome(chrome_path: str, html_pages: list[str]) -> list[str]:
    site_dir = os.path.join(os.getcwd(), "site")
    out_dir = os.path.join(site_dir, "pdfs_nohdr")
    os.makedirs(out_dir, exist_ok=True)

    pdfs: list[str] = []
    for html in html_pages:
        html_path = os.path.join(site_dir, html)
        if not os.path.exists(html_path):
            # Skip missing pages (e.g., reference overview)
            continue
        pdf_name = html.replace("/", "_").replace(".html", ".pdf")
        out_path = os.path.join(out_dir, pdf_name)
        url = f"file://{html_path}"
        cmd = [
            chrome_path,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            f"--print-to-pdf={out_path}",
            "--print-to-pdf-no-header",
            url,
        ]
        subprocess.run(cmd, check=True)
        pdfs.append(out_path)
    return pdfs


def ensure_playwright_browser() -> None:
    try:
        import playwright  # type: ignore
        # Install chromium if missing
        run([sys.executable, "-m", "playwright", "install", "chromium"])
    except Exception as e:
        raise SystemExit(f"Playwright not available or install failed: {e}")


def export_pdfs_playwright(html_pages: list[str]) -> list[str]:
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except Exception as e:
        raise SystemExit(f"Playwright import failed: {e}")

    site_dir = os.path.join(os.getcwd(), "site")
    out_dir = os.path.join(site_dir, "pdfs_nohdr")
    os.makedirs(out_dir, exist_ok=True)

    pdfs: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()
        for html in html_pages:
            html_path = os.path.join(site_dir, html)
            if not os.path.exists(html_path):
                continue
            pdf_name = html.replace("/", "_").replace(".html", ".pdf")
            out_path = os.path.join(out_dir, pdf_name)
            page.goto(f"file://{html_path}")
            page.pdf(path=out_path, print_background=True, display_header_footer=False)
            pdfs.append(out_path)
        browser.close()
    return pdfs


def merge_ordered(pdfs: list[str], output_path: str) -> None:
    writer = PdfWriter()
    added = 0
    for pdf in pdfs:
        reader = PdfReader(pdf)
        for page in reader.pages:
            writer.add_page(page)
        added += len(reader.pages)
    with open(output_path, "wb") as f:
        writer.write(f)
    print(f"Merged {added} pages into {output_path}")


def main() -> None:
    build_site()
    html_pages = list_pages()
    # Prefer Playwright for clean PDFs without headers/footers; fallback to Chrome CLI
    pdfs: list[str] = []
    try:
        ensure_playwright_browser()
        pdfs = export_pdfs_playwright(html_pages)
    except SystemExit:
        chrome = ensure_chrome()
        if not chrome:
            raise
        pdfs = export_pdfs_chrome(chrome, html_pages)
    if not pdfs:
        raise SystemExit("No PDFs generated")
    merge_ordered(pdfs, os.path.join("site", "Text2Everything-SDK-ordered.pdf"))


if __name__ == "__main__":
    main()


