#!/usr/bin/env python3
"""
SatSort - Static APT Repository Generator for GitHub Pages
Builds standard Debian APT repository hierarchy (pool/ and dists/)
and generates an attractive web landing page.
"""

import os
import sys
import gzip
import shutil
import hashlib
import subprocess
from datetime import datetime, timezone


def calculate_hash(file_path: str, algo: str) -> str:
    h = getattr(hashlib, algo)()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def extract_deb_control(deb_path: str) -> dict:
    res = subprocess.run(
        ["dpkg-deb", "-I", deb_path],
        capture_output=True,
        text=True,
        check=True,
    )
    info = {}
    current_key = None
    for line in res.stdout.splitlines():
        if line.startswith(" ") and current_key:
            info[current_key] += "\n" + line.strip()
        elif ":" in line:
            parts = line.split(":", 1)
            current_key = parts[0].strip()
            info[current_key] = parts[1].strip()
    return info


def build_repo(deb_dir: str, output_repo_dir: str):
    print(f"=== APT Deposu Oluşturuluyor: {output_repo_dir} ===")
    
    pool_dir = os.path.join(output_repo_dir, "pool", "main", "s", "satsort")
    dists_binary_dir = os.path.join(output_repo_dir, "dists", "stable", "main", "binary-amd64")
    dists_stable_dir = os.path.join(output_repo_dir, "dists", "stable")
    
    os.makedirs(pool_dir, exist_ok=True)
    os.makedirs(dists_binary_dir, exist_ok=True)

    deb_files = [f for f in os.listdir(deb_dir) if f.endswith(".deb")]
    if not deb_files:
        print(f"Uyarı: {deb_dir} içinde .deb dosyası bulunamadı!")
        return

    packages_entries = []

    for deb_name in sorted(deb_files):
        src_deb = os.path.join(deb_dir, deb_name)
        dst_deb = os.path.join(pool_dir, deb_name)
        shutil.copy2(src_deb, dst_deb)
        
        control = extract_deb_control(src_deb)
        size_bytes = os.path.getsize(src_deb)
        sha256 = calculate_hash(src_deb, "sha256")
        sha1 = calculate_hash(src_deb, "sha1")
        md5 = calculate_hash(src_deb, "md5")
        
        entry_lines = [
            f"Package: {control.get('Package', 'satsort')}",
            f"Version: {control.get('Version', '1.0.0')}",
            f"Architecture: {control.get('Architecture', 'amd64')}",
            f"Maintainer: {control.get('Maintainer', 'Gökcan <https://github.com/gokcank>')}",
            f"Installed-Size: {control.get('Installed-Size', '80000')}",
            f"Depends: {control.get('Depends', 'libc6')}",
            f"Section: {control.get('Section', 'video')}",
            f"Priority: {control.get('Priority', 'optional')}",
            f"Filename: pool/main/s/satsort/{deb_name}",
            f"Size: {size_bytes}",
            f"SHA256: {sha256}",
            f"SHA1: {sha1}",
            f"MD5sum: {md5}",
            f"Description: {control.get('Description', 'Modern Linux Native SatcoDX Channel List Editor')}",
        ]
        packages_entries.append("\n".join(entry_lines))

    # Write Packages & Packages.gz
    packages_content = "\n\n".join(packages_entries) + "\n"
    packages_file = os.path.join(dists_binary_dir, "Packages")
    packages_gz_file = os.path.join(dists_binary_dir, "Packages.gz")
    
    with open(packages_file, "w", encoding="utf-8") as f:
        f.write(packages_content)
        
    with gzip.open(packages_gz_file, "wb") as f:
        f.write(packages_content.encode("utf-8"))

    # Generate Release file
    now_utc = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S UTC")
    
    pkg_rel_path = "main/binary-amd64/Packages"
    pkg_gz_rel_path = "main/binary-amd64/Packages.gz"
    
    pkg_size = os.path.getsize(packages_file)
    pkg_sha256 = calculate_hash(packages_file, "sha256")
    pkg_md5 = calculate_hash(packages_file, "md5")
    
    pkg_gz_size = os.path.getsize(packages_gz_file)
    pkg_gz_sha256 = calculate_hash(packages_gz_file, "sha256")
    pkg_gz_md5 = calculate_hash(packages_gz_file, "md5")

    release_content = f"""Origin: SatSort Repository
Label: SatSort
Suite: stable
Codename: stable
Version: 1.0
Architectures: amd64
Components: main
Description: Official APT Repository for SatSort Channel Editor
Date: {now_utc}
MD5Sum:
 {pkg_md5} {pkg_size} {pkg_rel_path}
 {pkg_gz_md5} {pkg_gz_size} {pkg_gz_rel_path}
SHA256:
 {pkg_sha256} {pkg_size} {pkg_rel_path}
 {pkg_gz_sha256} {pkg_gz_size} {pkg_gz_rel_path}
"""
    release_file = os.path.join(dists_stable_dir, "Release")
    with open(release_file, "w", encoding="utf-8") as f:
        f.write(release_content)

    # Generate modern HTML landing page
    html_content = """<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SatSort - Linux APT Deposu</title>
  <style>
    :root {
      --bg: #0f172a;
      --card-bg: #1e293b;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --accent: #38bdf8;
      --accent-hover: #0284c7;
      --border: #334155;
      --code-bg: #0b1120;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.6;
      padding: 40px 20px;
    }
    .container {
      max-width: 800px;
      margin: 0 auto;
    }
    .header {
      text-align: center;
      margin-bottom: 40px;
    }
    .logo {
      width: 96px;
      height: 96px;
      margin-bottom: 16px;
    }
    h1 {
      font-size: 2.5rem;
      font-weight: 800;
      color: var(--accent);
      margin-bottom: 8px;
    }
    p.subtitle {
      font-size: 1.1rem;
      color: var(--text-muted);
    }
    .card {
      background-color: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 28px;
      margin-bottom: 24px;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    h2 {
      font-size: 1.3rem;
      margin-bottom: 16px;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    pre {
      background-color: var(--code-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
      overflow-x: auto;
      font-family: "JetBrains Mono", Consolas, monospace;
      font-size: 0.95rem;
      color: #38bdf8;
      margin-bottom: 12px;
    }
    .btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background-color: var(--accent);
      color: #0f172a;
      font-weight: 600;
      padding: 10px 20px;
      border-radius: 8px;
      text-decoration: none;
      transition: background-color 0.2s;
    }
    .btn:hover {
      background-color: var(--accent-hover);
    }
    .footer {
      text-align: center;
      margin-top: 40px;
      color: var(--text-muted);
      font-size: 0.9rem;
    }
    .footer a {
      color: var(--accent);
      text-decoration: none;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🛰️ SatSort</h1>
      <p class="subtitle">Modern Linux Native SatcoDX (.sdx) Uydu Kanal Listesi Düzenleyici</p>
    </div>

    <div class="card">
      <h2>📦 APT Deposu ile Kurulum (Ubuntu / Debian / Pardus / Mint)</h2>
      <p style="margin-bottom: 12px; color: var(--text-muted);">
        Depoyu sisteminize ekleyerek SatSort'u tek komutla kurabilir ve otomatik güncellemeleri alabilirsiniz:
      </p>
      <pre><code># 1. SatSort APT deposunu ekleyin
echo "deb [trusted=yes] https://gokcank.github.io/SatSort stable main" | sudo tee /etc/apt/sources.list.d/satsort.list

# 2. Paket listesini güncelleyip kurun
sudo apt update
sudo apt install satsort</code></pre>
    </div>

    <div class="card">
      <h2>🚀 Diğer Dağıtım Seçenekleri</h2>
      <p style="margin-bottom: 16px; color: var(--text-muted);">
        Kurulum yapmadan tek tıkla çalıştırmak isterseniz Evrensel <strong>AppImage</strong> paketini veya taşınabilir ikili dosyayı GitHub üzerinden indirebilirsiniz.
      </p>
      <a href="https://github.com/gokcank/SatSort/releases/latest" class="btn" target="_blank">
        📦 GitHub Releases Sayfasına Git
      </a>
    </div>

    <div class="footer">
      Geliştirici: <a href="https://github.com/gokcank" target="_blank">Gökcan</a> | 
      Kaynak Kodu: <a href="https://github.com/gokcank/SatSort" target="_blank">GitHub</a> | 
      Lisans: MIT
    </div>
  </div>
</body>
</html>
"""
    with open(os.path.join(output_repo_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content)

    # Touch .nojekyll to prevent Jekyll from filtering files
    with open(os.path.join(output_repo_dir, ".nojekyll"), "w") as f:
        pass

    print("✅ APT deposu ve karşılama sayfası başarıyla oluşturuldu!")


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "release_output"
    out = sys.argv[2] if len(sys.argv) > 2 else "apt_repo_out"
    build_repo(src, out)
