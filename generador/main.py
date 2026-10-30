"""Genera els calendaris (.ics), en català i en castellà, i la pàgina web a la carpeta de sortida.

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

TEXTOS = {
    'ca': dict(
        peu="Calendari romà general amb el propi d'Espanya, de Catalunya i de la diòcesi de Sant Feliu de Llobregat.",
        signatura=" Elaborat per {autor}.", periode="del {a} al {b}",
        fitxers={
            'liturgia-i-cami.ics': ('Litúrgia i Camí', "Calendari litúrgic en català i dates del Camí Neocatecumenal, {p}.{s}", 'tot'),
        }),
    'es': dict(
        peu="Calendario romano general con el propio de España, de Cataluña y de la diócesis de Sant Feliu de Llobregat.",
        signatura=" Elaborado por {autor}.", periode="del {a} al {b}",
        fitxers={
            'calendario-es.ics': ('Liturgia y Camino', "Calendario litúrgico en castellano y fechas del Camino Neocatecumenal, {p}.{s}", 'tot'),
        }),
}


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

    llegeix = lambda nom: yaml.safe_load((ARREL / 'dades' / nom).read_text(encoding='utf-8')) or []  # noqa: E731
    propi, entrades_cami = llegeix('propi.yaml'), llegeix('cami.yaml')
    locals_ = llegeix('locals.yaml') if (ARREL / 'dades' / 'locals.yaml').exists() else []
    config = llegeix('config.yaml') or {}
    autor = config.get('autor') or ''

    resum, avisos_tots = {}, []
    for lang, tx in TEXTOS.items():
        dies, trams, avisos = liturgia.genera(raw, anys, propi, emojis=bool(config.get('emojis')),
                                              sigles=bool(config.get('sigles')), lang=lang)
        avisos_tots += avisos if lang == 'ca' else []
        inici, fi = dies[0]['data'], dies[-1]['data']
        signatura = tx['signatura'].format(autor=autor) if autor else ''
        pre = (lang,) if lang != 'ca' else ()
        ev_lit = [ics.vevent(ics.uid(*pre, 'dia', x['data']), x['data'], x['data'] + dt.timedelta(1),
                             x['titol'], x['desc'] + '\n\n' + tx['peu'] + signatura) for x in dies if not x['buit']]
        ev_lit += [ics.vevent(ics.uid(*pre, 'temps', t['ini']), t['ini'], t['fi'] + dt.timedelta(1),
                              t['nom'], t['desc']) for t in trams]
        ev_lit += cami.genera(locals_, inici, fi, prefix='local', lang=lang)
        ev_cami = cami.genera(entrades_cami, inici, fi, lang=lang)
        grups = {'tot': ev_lit + ev_cami, 'lit': ev_lit, 'cami': ev_cami}
        periode = tx['periode'].format(a=f"{inici:%d/%m/%Y}", b=f"{fi:%d/%m/%Y}")
        for nom, (titol, descripcio, grup) in tx['fitxers'].items():
            (sortida / nom).write_text(
                ics.calendari(titol, descripcio.format(p=periode, s=signatura), grups[grup]),
                encoding='utf-8', newline='')
            resum[nom] = len(grups[grup])

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
        'esdeveniments': resum,
    }, ensure_ascii=False, indent=1), encoding='utf-8')

    print(f"Període: {inici:%d/%m/%Y} - {fi:%d/%m/%Y} (cursos {', '.join(f'{y - 1}-{str(y)[2:]}' for y in anys)})")
    for k, v in resum.items():
        print(f"  {k}: {v} esdeveniments")
    for av in avisos_tots:
        print('  ·', av)


if __name__ == '__main__':
    main()
