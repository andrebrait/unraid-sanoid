#!/usr/bin/env python3
import hashlib
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parent.parent
manifest = ET.parse(root / 'sanoid.plg').getroot()
packages = [file for file in manifest.findall('FILE') if file.find('URL') is not None]
if not packages:
    sys.exit('No downloadable packages found in sanoid.plg')

for file in packages:
    url = file.findtext('URL')
    expected = file.findtext('SHA256')
    package = root / 'packages' / Path(url).name
    if not expected or not package.is_file():
        sys.exit(f'Missing package or SHA256: {url}')
    actual = hashlib.sha256(package.read_bytes()).hexdigest()
    if actual != expected:
        sys.exit(f'SHA256 mismatch: {package.name}')
    print(f'{package.name}: OK')
