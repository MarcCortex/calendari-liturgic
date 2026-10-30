"""Genera els tres calendaris (.ics) i la pàgina web a la carpeta de sortida.

Ús:  python generador/main.py [--sortida public] [--avui AAAA-MM-DD]
"""
import argparse
import datetime as dt
import json
import pathlib
import shutil
import subprocess
import sys
import zoneinfo

import yaml

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import cami  # noqa: E402
import ics  # noqa: E402
import liturgia  # noqa: E402

# Quants anys litúrgics es publiquen: l'actual, els que hi ha al darrere i els que vénen.
ANYS_ENRERE = 0
ANYS_ENDAVANT = 3

ARREL = pathlib.Path(__file__).resolve().parent.parent
PEU = ("\n\nCalendari romà general amb el propi d'Espanya, de Catalunya i de la diòcesi de Sant Feliu "
       "de Llobregat.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sortida', default='public')
    ap.add_argument('--avui', help='data de referència (per fer proves)')
    a = ap.parse_args()

    avui = (dt.date.fromisoformat(a.avui) if a.avui
            else dt.datetime.now(zoneinfo.ZoneInfo('Europe/Madrid')).date())
    actual = liturgia.any_liturgic(avui)
    anys = list(range(actual - ANYS_ENRERE, actual + ANYS_ENDAVANT + 1))
    sortida = (ARREL / a.sortida) if not pathlib.Path(a.sortida).is_absolute() else pathlib.Path(a.sortida)
    sortida.mkdir(parents=True, exist_ok=True)

    tmp = sortida / '_romcal.json'
    subprocess.run(['node', str(ARREL / 'romcal_dump.mjs'), str(tmp), *map(str, anys)], check=True, cwd=ARREL)
    raw = json.loads(tmp.read_text())
    tmp.unlink()

    propi = yaml.safe_load((ARREL / 'dades' / 'propi.yaml').read_text(encoding='utf-8'))
    config = yaml.safe_load((ARREL / 'dades' / 'config.yaml').read_text(encoding='utf-8')) or {}
    autor = config.get('autor') or ''
    signatura = f" Elaborat per {autor}." if autor else ''
    entrades_cami = yaml.safe_load((ARREL / 'dades' / 'cami.yaml').read_text(encoding='utf-8')) or []

    dies, trams, avisos = liturgia.genera(raw, anys, propi, emojis=bool(config.get('emojis')),
                                          sigles=bool(config.get('sigles')))
    inici, fi = dies[0]['data'], dies[-1]['data']
    ev_lit = [ics.vevent(ics.uid('dia', x['data']), x['data'], x['data'] + dt.timedelta(1),
                         x['titol'], x['desc'] + PEU + signatura) for x in dies]
    ev_lit += [ics.vevent(ics.uid('temps', t['ini']), t['ini'], t['fi'] + dt.timedelta(1), t['nom'],
                          f"Del {t['ini']:%d/%m/%Y} al {t['fi']:%d/%m/%Y}.") for t in trams]
    ev_cami = cami.genera(entrades_cami, inici, fi)
    # Celebracions locals (dades/locals.yaml): van al calendari de Litúrgia com a esdeveniments a part
    fitxer_locals = ARREL / 'dades' / 'locals.yaml'
    if fitxer_locals.exists():
        ev_lit += cami.genera(yaml.safe_load(fitxer_locals.read_text(encoding='utf-8')) or [], inici, fi, prefix='local')

    periode = f"del {inici:%d/%m/%Y} al {fi:%d/%m/%Y}"
    fitxers = {
        'liturgia.ics': ('Litúrgia', f"Calendari litúrgic en català (Catalunya, diòcesi de Sant Feliu de Llobregat), {periode}.{signatura}", ev_lit),
        'cami.ics': ('Camí Neocatecumenal', f"Dates i aniversaris del Camí Neocatecumenal, {periode}.{signatura}", ev_cami),
        'liturgia-i-cami.ics': ('Litúrgia i Camí', f"Calendari litúrgic i dates del Camí Neocatecumenal, {periode}.{signatura}", ev_lit + ev_cami),
    }
    for nom, (titol, descripcio, evs) in fitxers.items():
        (sortida / nom).write_text(ics.calendari(titol, descripcio, evs), encoding='utf-8', newline='')

    for f in (ARREL / 'web').iterdir():
        shutil.copy(f, sortida / f.name)
    codi_gc = str(config.get('goatcounter') or '').strip()
    if codi_gc:  # comptador de visites i de clics (goatcounter.com)
        index = sortida / 'index.html'
        index.write_text(index.read_text(encoding='utf-8').replace(
            '<!-- GOATCOUNTER -->',
            f'<script data-goatcounter="https://{codi_gc}.goatcounter.com/count" async '
            f'src="https://gc.zgo.at/count.js"></script>'), encoding='utf-8')
    (sortida / 'info.json').write_text(json.dumps({
        'generat': dt.datetime.now(zoneinfo.ZoneInfo('Europe/Madrid')).strftime('%d/%m/%Y %H:%M'),
        'autor': autor,
        'inici': f"{inici:%d/%m/%Y}", 'fi': f"{fi:%d/%m/%Y}",
        'cursos': [f"{y - 1}-{str(y)[2:]}" for y in anys],
        'esdeveniments': {k: len(v[2]) for k, v in fitxers.items()},
    }, ensure_ascii=False, indent=1), encoding='utf-8')

    print(f"Període: {periode} (cursos {', '.join(f'{y - 1}-{str(y)[2:]}' for y in anys)})")
    for k, v in fitxers.items():
        print(f"  {k}: {len(v[2])} esdeveniments")
    for av in avisos:
        print('  ·', av)


if __name__ == '__main__':
    main()
