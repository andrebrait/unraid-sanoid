#!/usr/bin/env python3
import hashlib
import re
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parent.parent
manifest = ET.parse(root / 'sanoid.plg').getroot()
packages = [file for file in manifest.findall('FILE') if file.find('URL') is not None]
if not packages:
    sys.exit('No downloadable packages found in sanoid.plg')

scripts = [file.findtext('INLINE', '') for file in manifest.findall('FILE')]
lists = [match.group(1).split() for script in scripts
         if (match := re.search(r'PACKAGES="(.*?)"', script, re.S))]
names = [Path(file.get('Name', '')).name for file in packages]
if len(lists) != 1 or len(names) != len(set(names)) or set(lists[0]) != set(names):
    sys.exit('Installed packages do not match verified manifest files')

for file in packages:
    url = file.findtext('URL')
    if Path(file.get('Name', '')).name != Path(url).name:
        sys.exit(f'Package name does not match URL: {url}')
    expected = file.findtext('SHA256')
    package = root / 'packages' / Path(url).name
    if not expected or not package.is_file():
        sys.exit(f'Missing package or SHA256: {url}')
    actual = hashlib.sha256(package.read_bytes()).hexdigest()
    if actual != expected:
        sys.exit(f'SHA256 mismatch: {package.name}')
    print(f'{package.name}: OK')
