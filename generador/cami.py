"""Esdeveniments del Camí Neocatecumenal a partir de dades/cami.yaml."""
import datetime as dt

import ics


def ordinal(n):
    return {1: '1r', 2: '2n', 3: '3r', 4: '4t'}.get(n, f'{n}è')


def genera(entrades, inici, fi, prefix='cami'):
    events = []
    for e in entrades:
        d0 = e['data'] if isinstance(e['data'], dt.date) else dt.date.fromisoformat(str(e['data']))
        desc = (e.get('descripcio') or '').strip()
        if e.get('font'):
            desc += f"\n\nFont: {e['font']}"
        if e.get('repeteix', True):
            for y in range(inici.year, fi.year + 1):
                try:
                    d = d0.replace(year=y)
                except ValueError:  # 29 de febrer
                    d = dt.date(y, 2, 28)
                n = y - d0.year
                if inici <= d <= fi and n > 0:
                    events.append((d, e['titol'].replace('{n}', ordinal(n)), desc, (prefix, d0, y)))
        elif inici <= d0 <= fi:
            events.append((d0, e['titol'].replace(' ({n} aniversari)', '').replace('{n}', ''), desc, (prefix, d0, e['titol'])))
    events.sort(key=lambda t: t[0])
    return [ics.vevent(ics.uid(*clau), d, d + dt.timedelta(1), titol, desc) for d, titol, desc, clau in events]
