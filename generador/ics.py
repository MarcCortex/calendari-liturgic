"""Utilitats per escriure fitxers iCalendar (RFC 5545)."""
import datetime as dt
import hashlib

SUFIX_UID = '@liturgia-cat'
# Color suggerit (to "flamenc" de Google Calendar). L'Apple Calendar el fa servir; Google l'ignora.
COLOR = '#E67C73'
COLOR_CSS = 'salmon'


def esc(t):
    return t.replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,').replace('\n', '\\n')


def fold(line):
    """Talla les línies a 75 octets, com demana l'estàndard."""
    out, cur = [], b''
    for ch in line:
        cb = ch.encode('utf-8')
        if len(cur) + len(cb) > (75 if not out else 74):
            out.append(cur)
            cur = b''
        cur += cb
    out.append(cur)
    return '\r\n '.join(x.decode('utf-8') for x in out)


def uid(*parts):
    return hashlib.sha1('|'.join(map(str, parts)).encode()).hexdigest()[:20] + SUFIX_UID


_STAMP = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')


def vevent(id_, ini, fi_exclusiu, titol, desc):
    linies = ['BEGIN:VEVENT', f'UID:{id_}', f'DTSTAMP:{_STAMP}',
              f'DTSTART;VALUE=DATE:{ini:%Y%m%d}', f'DTEND;VALUE=DATE:{fi_exclusiu:%Y%m%d}',
              f'SUMMARY:{esc(titol)}', f'DESCRIPTION:{esc(desc)}', 'TRANSP:TRANSPARENT', 'END:VEVENT']
    return [fold(l) for l in linies]


def calendari(nom, descripcio, events):
    linies = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//calendari-liturgic//CA', 'CALSCALE:GREGORIAN',
              'METHOD:PUBLISH', fold(f'X-WR-CALNAME:{esc(nom)}'), 'X-WR-TIMEZONE:Europe/Madrid',
              fold(f'X-WR-CALDESC:{esc(descripcio)}'),
              'REFRESH-INTERVAL;VALUE=DURATION:PT12H', 'X-PUBLISHED-TTL:PT12H',
              f'X-APPLE-CALENDAR-COLOR:{COLOR}', f'COLOR:{COLOR_CSS}']
    for e in events:
        linies += e
    linies.append('END:VCALENDAR')
    return '\r\n'.join(linies) + '\r\n'
