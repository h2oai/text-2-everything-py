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


def list_pages_with_sections() -> list[dict]:
    with open("mkdocs.yml", "r") as f:
        cfg = yaml.safe_load(f)
    nav = cfg.get("nav", [])
    items: list[dict] = []

    def add_page(path: str, section: str) -> None:
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
            items.append({"kind": "page", "html": filename, "section": section})

    def slugify(text: str) -> str:
        return "".join(c.lower() if c.isalnum() else "-" for c in text).strip("-")

    # Simple intros per section
    section_intros = {
        "Guides": (
            "In-depth articles for each SDK resource. Learn capabilities, required parameters,"
            " common patterns, and best practices with end-to-end examples."
        ),
        "How To": (
            "Task-focused recipes to accomplish common goals quickly. Copy, paste, and adapt"
            " minimal snippets with clear pre-requisites and expected results."
        ),
        "Performance": (
            "Guidance for high-throughput and long-running workloads. Tune timeouts, connection"
            " pools, concurrency, and follow testing strategies for reliable performance."
        ),
        "Reference": (
            "API reference. Use this section to find exact class"
            " and method signatures, parameters, return types, and model schemas."
        ),
        "Migrations": (
            "Version-to-version changes, deprecations, and safe update steps. Includes example"
            " diffs and code updates to migrate with confidence."
        ),
        "Troubleshooting": (
            "Common errors, diagnostics, and remedies. Map SDK exceptions to causes and actions,"
            " and learn how to capture useful context for support."
        ),
        "Examples": (
            "Executable notebooks and concise samples that demonstrate complete workflows—from"
            " setup to SQL generation and execution."
        ),
    }

    for item in nav:
        if isinstance(item, dict):
            for title, value in item.items():
                if isinstance(value, str):
                    # Top-level single page: its own section
                    add_page(value, title)
                elif isinstance(value, list):
                    # Insert a section divider before grouped pages
                    items.append({
                        "kind": "section",
                        "title": title,
                        "slug": slugify(title),
                        "intro": section_intros.get(title, f"Section: {title}"),
                    })
                    for sub in value:
                        if isinstance(sub, dict):
                            for __, spath in sub.items():
                                if isinstance(spath, str):
                                    add_page(spath, title)
    return items


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


def export_pdfs_playwright(items: list[dict]) -> list[str]:
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
        for it in items:
            if it.get("kind") == "section":
                title = it["title"]
                intro = it.get("intro", "")
                slug = it["slug"]
                pdf_name = f"section_{slug}.pdf"
                out_path = os.path.join(out_dir, pdf_name)
                html = f"""
                <html>
                <head>
                  <meta charset=\"utf-8\" />
                  <style>
                    html, body {{ height:100%; margin:0; }}
                    body {{ font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; }}
                    .wrap {{ height:100%; display:flex; flex-direction:column; justify-content:center; align-items:center; padding:48px; }}
                    h1 {{ font-size: 42px; margin: 0 0 8px 0; }}
                    p {{ font-size: 16px; color:#444; max-width: 720px; text-align:center; margin: 0; }}
                  </style>
                </head>
                <body>
                  <div class=\"wrap\">
                    <h1>{title}</h1>
                    <p>{intro}</p>
                  </div>
                </body>
                </html>
                """
                page.set_content(html)
                # Divider page: no header needed
                page.pdf(
                    path=out_path,
                    print_background=True,
                    display_header_footer=False,
                )
                pdfs.append(out_path)
            else:
                html = it["html"]
                html_path = os.path.join(site_dir, html)
                if not os.path.exists(html_path):
                    continue
                pdf_name = html.replace("/", "_").replace(".html", ".pdf")
                out_path = os.path.join(out_dir, pdf_name)
                section = it.get("section", "")
                page.goto(f"file://{html_path}")
                header_html = f'''
                <div style="font-size:10px; color:#666; width:100%; padding:6px 12px;">
                  {section}
                </div>
                '''
                page.pdf(
                    path=out_path,
                    print_background=True,
                    display_header_footer=True,
                    header_template=header_html,
                    footer_template='<div></div>',
                    margin={"top": "28px", "bottom": "16px"},
                )
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
    items = list_pages_with_sections()
    # Prefer Playwright for clean PDFs without headers/footers; fallback to Chrome CLI
    pdfs: list[str] = []
    try:
        ensure_playwright_browser()
        pdfs = export_pdfs_playwright(items)
    except SystemExit:
        chrome = ensure_chrome()
        if not chrome:
            raise
        # Map back to only page items for Chrome fallback
        html_pages = [it["html"] for it in items if it.get("kind") == "page"]
        pdfs = export_pdfs_chrome(chrome, html_pages)
    if not pdfs:
        raise SystemExit("No PDFs generated")
    merge_ordered(pdfs, os.path.join("site", "Text2Everything-SDK-ordered.pdf"))


if __name__ == "__main__":
    main()


