"""Read installed Windows fonts and explicitly included local game fonts."""
from functools import lru_cache
import hashlib
import os
from pathlib import Path
import struct
try:
    import winreg
except ImportError:  # Linux/macOS deployments use directory discovery.
    winreg = None

from PIL import ImageFont
from fontTools.ttLib import TTFont

FONT_SUFFIXES = {'.ttf', '.otf', '.ttc', '.otc'}
SYSTEM_FONTS = Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts'
USER_FONTS = Path(os.environ.get('LOCALAPPDATA', str(Path.home() / 'AppData/Local'))) / 'Microsoft/Windows/Fonts'


def installed_files():
    files = set()
    for directory in [SYSTEM_FONTS, USER_FONTS]:
        if directory.exists():
            files.update(p.resolve() for p in directory.iterdir() if p.suffix.lower() in FONT_SUFFIXES and p.is_file())
    if winreg is not None:
        registry_path = r'SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts'
        for hive in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
            try:
                with winreg.OpenKey(hive, registry_path) as key:
                    for i in range(winreg.QueryInfoKey(key)[1]):
                        _, value, _ = winreg.EnumValue(key, i)
                        if not isinstance(value, str):
                            continue
                        path = Path(os.path.expandvars(value))
                        candidates = [path] if path.is_absolute() else [SYSTEM_FONTS/path, USER_FONTS/path]
                        files.update(p.resolve() for p in candidates if p.suffix.lower() in FONT_SUFFIXES and p.is_file())
            except OSError:
                pass
    else:
        for directory in [Path('/usr/share/fonts'), Path('/usr/local/share/fonts'),
                          Path('/System/Library/Fonts'), Path('/Library/Fonts'),
                          Path.home()/'.local/share/fonts', Path.home()/'.fonts', Path.home()/'Library/Fonts']:
            if directory.is_dir():
                files.update(p.resolve() for p in directory.rglob('*')
                             if p.suffix.lower() in FONT_SUFFIXES and p.is_file())
    return sorted(files, key=lambda p: str(p).casefold())


def name_value(font, name_id, chinese=False):
    records = [n for n in font['name'].names if n.nameID == name_id]
    records.sort(key=lambda n: (0 if n.langID == (0x804 if chinese else 0x409) else 1 if n.langID == 0x409 else 2,
                                0 if n.platformID == 3 else 1))
    for record in records:
        try:
            text = record.toUnicode().strip()
            if text:
                return text
        except (UnicodeError, LookupError):
            pass
    return ''


def enumerate_fonts(additional_files=(), *, include_system=True):
    result = []
    seen = set()
    for path in list(dict.fromkeys([Path(p).resolve() for p in additional_files] + (installed_files() if include_system else []))):
        try:
            with path.open('rb') as file:
                header = file.read(12)
            faces = struct.unpack('>I', header[8:12])[0] if header[:4] == b'ttcf' else 1
            if not 1 <= faces <= 128:
                continue
            for index in range(faces):
                try:
                    # Only offer faces the export renderer can actually load.
                    pillow = ImageFont.truetype(str(path), 13, index=index)
                    family, face = pillow.getname()
                    with TTFont(str(path), fontNumber=index, lazy=True) as font:
                        localized_family = name_value(font, 16, True) or name_value(font, 1, True) or family
                        localized_face = name_value(font, 17, True) or name_value(font, 2, True) or face
                        full_name = name_value(font, 4) or (family if face == 'Regular' else family+' '+face)
                        postscript = name_value(font, 6)
                    identity = postscript or full_name
                    if identity in seen:
                        continue
                    seen.add(identity)
                    identifier = hashlib.sha256((str(path).casefold()+':'+str(index)).encode()).hexdigest()[:16]
                    regular = localized_face.casefold() in ['regular', 'normal', '常规', '标准', '標準', '標準體']
                    result.append(dict(id=identifier, family=family, face=face,
                                       label=localized_family if regular else localized_family+' · '+localized_face,
                                       fullName=full_name, postscriptName=postscript,
                                       path=str(path), index=index))
                except (OSError, ValueError, KeyError, struct.error):
                    continue
        except (OSError, struct.error):
            continue
    result.sort(key=lambda f: (f['label'].casefold(), f['fullName'].casefold()))
    return result


@lru_cache(maxsize=128)
def glyphs(path, index):
    with TTFont(path, fontNumber=index, lazy=True) as font:
        return frozenset((font.getBestCmap() or {}).keys())


@lru_cache(maxsize=256)
def load_font(path, index, size):
    return ImageFont.truetype(path, size, index=index)


def text_runs(text, selected, fallback, size):
    primary = load_font(selected['path'], selected['index'], size)
    secondary = load_font(fallback['path'], fallback['index'], size)
    coverage = glyphs(selected['path'], selected['index'])
    fallback_coverage = glyphs(fallback['path'], fallback['index'])
    runs = []
    for char in text:
        chosen = primary if ord(char) in coverage or ord(char) not in fallback_coverage else secondary
        if runs and runs[-1][1] is chosen:
            runs[-1] = (runs[-1][0]+char, chosen)
        else:
            runs.append((char, chosen))
    return runs
