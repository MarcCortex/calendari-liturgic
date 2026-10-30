"""Esdeveniments que es repeteixen cada any (dades/cami.yaml, dades/locals.yaml)."""
import datetime as dt

import ics

TEXT = {'ca': dict(font='Font', aniv=' ({n} aniversari)'),
        'es': dict(font='Fuente', aniv=' ({n} aniversario)')}


def ordinal(n, lang='ca'):
    if lang == 'es':
        return f'{n}.º'
    return {1: '1r', 2: '2n', 3: '3r', 4: '4t'}.get(n, f'{n}è')


def genera(entrades, inici, fi, prefix='cami', lang='ca'):
    t = TEXT[lang]
    events = []
    for e in entrades:
        d0 = e['data'] if isinstance(e['data'], dt.date) else dt.date.fromisoformat(str(e['data']))
        titol = (e.get('titol_es') or e['titol']) if lang == 'es' else e['titol']
        desc = (((e.get('descripcio_es') or e.get('descripcio')) if lang == 'es' else e.get('descripcio')) or '').strip()
        if e.get('font'):
            desc += f"\n\n{t['font']}: {e['font']}"
        if e.get('repeteix', True):
            for y in range(inici.year, fi.year + 1):
                try:
                    d = d0.replace(year=y)
                except ValueError:  # 29 de febrer
                    d = dt.date(y, 2, 28)
                n = y - d0.year
                if inici <= d <= fi and n > 0:
                    events.append((d, titol.replace('{n}', ordinal(n, lang)), desc, (prefix, d0, y)))
        elif inici <= d0 <= fi:
            net = titol.replace(TEXT['ca']['aniv'], '').replace(TEXT['es']['aniv'], '').replace('{n}', '')
            events.append((d0, net, desc, (prefix, d0, e['titol'])))
    events.sort(key=lambda x: x[0])
    pre = (lang,) if lang != 'ca' else ()
    return [ics.vevent(ics.uid(*pre, *clau), d, d + dt.timedelta(1), titol, desc) for d, titol, desc, clau in events]
