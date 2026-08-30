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
        ["dpkg-deb", "-f", deb_path],
        capture_output=True,
        text=True,
        check=True,
    )
    info = {}
    current_key = None
    for line in res.stdout.splitlines():
        if (line.startswith(" ") or line.startswith("\t")) and current_key:
            info[current_key] += "\n " + line.strip()
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

    deb_files = [f for f in os.listdir(deb_dir) if f.endswith(".deb")] if os.path.exists(deb_dir) else []
    if not deb_files:
        print(f"Uyarı: {deb_dir} içinde .deb dosyası bulunamadı!")
    else:
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

        # Extract version with filename fallback if needed
        deb_ver = control.get('Version')
        if not deb_ver and '_' in deb_name:
            deb_ver = deb_name.split('_')[1]
        if not deb_ver:
            deb_ver = '1.1.0'

        # Format multiline description ensuring Debian policy compliant leading spaces
        raw_desc = control.get('Description', 'Modern Linux Native SatcoDX Channel List Editor')
        desc_lines = []
        for i, l in enumerate(raw_desc.splitlines()):
            stripped = l.strip()
            if i == 0:
                desc_lines.append(stripped)
            else:
                desc_lines.append(f" {stripped}" if stripped else " .")
        formatted_desc = "\n".join(desc_lines)
        
        entry_lines = [
            f"Package: {control.get('Package', 'satsort')}",
            f"Version: {deb_ver}",
            f"Architecture: {control.get('Architecture', 'amd64')}",
            f"Maintainer: {control.get('Maintainer', 'gokcank <https://github.com/gokcank>')}",
            f"Installed-Size: {control.get('Installed-Size', '80000')}",
            f"Depends: {control.get('Depends', 'libc6')}",
            f"Section: {control.get('Section', 'video')}",
            f"Priority: {control.get('Priority', 'optional')}",
            f"Filename: pool/main/s/satsort/{deb_name}",
            f"Size: {size_bytes}",
            f"SHA256: {sha256}",
            f"SHA1: {sha1}",
            f"MD5sum: {md5}",
            f"Description: {formatted_desc}",
        ]
        packages_entries.append("\n".join(entry_lines))

    if deb_files:
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

    # Copy modern product website assets from website/ directory
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    website_dir = os.path.join(repo_root, "website")

    if os.path.isdir(website_dir):
        print(f"-> Web sitesi dosyaları kopyalanıyor: {website_dir} -> {output_repo_dir}")
        for item in os.listdir(website_dir):
            src_path = os.path.join(website_dir, item)
            dst_path = os.path.join(output_repo_dir, item)
            if os.path.isfile(src_path):
                shutil.copy2(src_path, dst_path)
            elif os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
    else:
        print("Uyarı: website/ klasörü bulunamadı!")

    # Touch .nojekyll to prevent Jekyll from filtering files
    with open(os.path.join(output_repo_dir, ".nojekyll"), "w") as f:
        pass

    print("✅ APT deposu ve karşılama sayfası başarıyla oluşturuldu!")


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "release_output"
    out = sys.argv[2] if len(sys.argv) > 2 else "apt_repo_out"
    build_repo(src, out)
