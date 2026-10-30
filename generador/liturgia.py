"""Calendari litúrgic en català: propi del temps (calculat aquí) + santoral (romcal, Espanya)
+ propi de Catalunya i de la diòcesi (dades/propi.yaml)."""
import collections
import datetime as dt

from noms_ca import NOMS

D = dt.date
td = dt.timedelta


# ------------------------------------------------------------------ dates bàsiques
def pasqua(y):
    a = y % 19; b, c = divmod(y, 100); d, e = divmod(b, 4); f = (b + 8) // 25
    g = (b - f + 1) // 3; h = (19 * a + b - d - g + 15) % 30; i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7; m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31; dia = (h + l - 7 * m + 114) % 31 + 1
    return D(y, mes, dia)


def advent1(y):
    """Primer diumenge d'Advent de l'any civil y (quatre diumenges abans de Nadal)."""
    d = D(y, 12, 24)
    while d.weekday() != 6:
        d -= td(1)
    return d - td(21)


def any_liturgic(d):
    """Any en què acaba l'any litúrgic que conté la data d."""
    return d.year + 1 if d >= advent1(d.year) else d.year


def baptisme(y):
    d = D(y, 1, 7)
    while d.weekday() != 6:
        d += td(1)
    return d


DIES = ['Dilluns', 'Dimarts', 'Dimecres', 'Dijous', 'Divendres', 'Dissabte', 'Diumenge']
ROM = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII', 'XIV', 'XV',
       'XVI', 'XVII', 'XVIII', 'XIX', 'XX', 'XXI', 'XXII', 'XXIII', 'XXIV', 'XXV', 'XXVI', 'XXVII',
       'XXVIII', 'XXIX', 'XXX', 'XXXI', 'XXXII', 'XXXIII', 'XXXIV']
ORD_DIA = {26: '2n', 27: '3r', 28: '4t', 29: '5è', 30: '6è', 31: '7è'}
DA = "Durant l'any"


def propi_del_temps(d):
    """(temps, nom, precedència, color, setmana, clau). Precedència segons la taula de les
    Normes universals: 1 Tridu; 2 Nadal, Epifania, Ascensió, Pentecosta, diumenges d'Advent,
    Quaresma i Pasqua, Cendra, Setmana Santa, octava de Pasqua; 3 solemnitats; 5 festes del Senyor;
    6 diumenges de Nadal i de durant l'any; 9 fèries privilegiades; 13 fèries."""
    y = any_liturgic(d)
    A1 = advent1(y - 1); nadal = D(y - 1, 12, 25); ep = D(y, 1, 6); bapt = baptisme(y)
    P = pasqua(y); cendra = P - td(46); pent = P + td(49); rei = advent1(y) - td(7)
    dw = d.weekday(); dia = DIES[dw]

    if A1 <= d < nadal:
        k = (d - A1).days // 7 + 1
        if dw == 6:
            nom = f"Diumenge {ROM[k]} d'Advent" + (' (Gaudete)' if k == 3 else '')
            return ('Advent', nom, 2, 'ROSE' if k == 3 else 'PURPLE', f"{k}a setmana d'Advent", 'diumenge')
        if d.month == 12 and d.day >= 17:
            return ('Advent', f"Fèria privilegiada d'Advent ({d.day} de desembre)", 9, 'PURPLE', f"{k}a setmana d'Advent", 'feria')
        return ('Advent', f"{dia} de la {k}a setmana d'Advent", 13, 'PURPLE', f"{k}a setmana d'Advent", 'feria')
    if nadal <= d <= bapt:
        if d == nadal:
            return ('Nadal', 'La Nativitat del Senyor (Nadal)', 2, 'WHITE', 'Octava de Nadal', 'solemnitat')
        if d == D(y, 1, 1):
            return ('Nadal', 'Santa Maria, Mare de Déu (Octava de Nadal)', 3, 'WHITE', 'Octava de Nadal', 'solemnitat')
        if d == ep:
            return ('Nadal', "L'Epifania del Senyor", 2, 'WHITE', 'Temps de Nadal', 'solemnitat')
        if d == bapt:
            return ('Nadal', 'El Baptisme del Senyor', 5, 'WHITE', 'Temps de Nadal', 'festa')
        sf = next((nadal + td(i) for i in range(1, 7) if (nadal + td(i)).weekday() == 6), D(y - 1, 12, 30))
        if d == sf:
            return ('Nadal', 'La Sagrada Família de Jesús, Maria i Josep', 5, 'WHITE', 'Octava de Nadal', 'festa')
        if d.month == 12:
            return ('Nadal', f"{ORD_DIA[d.day]} dia de l'octava de Nadal", 9, 'WHITE', 'Octava de Nadal', 'feria')
        if d < ep:
            if dw == 6:
                return ('Nadal', 'Diumenge II després de Nadal', 6, 'WHITE', 'Temps de Nadal', 'diumenge')
            return ('Nadal', f"Fèria del temps de Nadal ({d.day} de gener)", 13, 'WHITE', 'Temps de Nadal', 'feria')
        return ('Nadal', f"{dia} després de l'Epifania", 13, 'WHITE', 'Temps de Nadal', 'feria')
    if bapt < d < cendra:
        k = (d - bapt).days // 7 + 1
        if dw == 6:
            nom = f"Diumenge {ROM[k]} de durant l'any" + (' · Diumenge de la Paraula de Déu' if k == 3 else '')
            return (DA, nom, 6, 'GREEN', f"{k}a setmana de durant l'any", 'diumenge')
        return (DA, f"{dia} de la {k}a setmana de durant l'any", 13, 'GREEN', f"{k}a setmana de durant l'any", 'feria')
    if cendra <= d < P - td(3):
        if d == cendra:
            return ('Quaresma', 'Dimecres de Cendra', 2, 'PURPLE', 'Inici de la Quaresma', 'feria-priv')
        if d < cendra + td(4):
            return ('Quaresma', f'{dia} després de Cendra', 9, 'PURPLE', 'Inici de la Quaresma', 'feria')
        k = (d - (cendra + td(4))).days // 7 + 1
        if k == 6:
            if dw == 6:
                return ('Quaresma', 'Diumenge de Rams de la Passió del Senyor', 2, 'RED', 'Setmana Santa', 'diumenge')
            return ('Quaresma', f'{dia} Sant', 2, 'PURPLE', 'Setmana Santa', 'feria-priv')
        if dw == 6:
            nom = f"Diumenge {ROM[k]} de Quaresma" + (' (Laetare)' if k == 4 else '')
            return ('Quaresma', nom, 2, 'ROSE' if k == 4 else 'PURPLE', f"{k}a setmana de Quaresma", 'diumenge')
        return ('Quaresma', f"{dia} de la {k}a setmana de Quaresma", 9, 'PURPLE', f"{k}a setmana de Quaresma", 'feria')
    if P - td(3) <= d <= P:
        noms = {3: ('Dijous Sant · Missa vespertina de la Cena del Senyor (inici del Tridu Pasqual)', 'WHITE'),
                2: ('Divendres Sant de la Passió del Senyor', 'RED'),
                1: ('Dissabte Sant · Vetlla Pasqual', 'WHITE'),
                0: ('Diumenge de Pasqua de la Resurrecció del Senyor', 'WHITE')}
        n, c = noms[(P - d).days]
        if d == P:
            return ('Pasqua', n, 1, c, 'Octava de Pasqua', 'solemnitat')
        return ('Tridu Pasqual', n, 1, c, 'Tridu Pasqual', 'tridu')
    if P < d <= pent:
        k = (d - P).days // 7 + 1
        if d == pent:
            return ('Pasqua', 'Diumenge de Pentecosta', 2, 'RED', 'Cloenda del temps de Pasqua', 'solemnitat')
        if d == P + td(42):
            return ('Pasqua', "L'Ascensió del Senyor (Diumenge VII de Pasqua)", 2, 'WHITE', '7a setmana de Pasqua', 'solemnitat')
        if k == 1:
            return ('Pasqua', f"{dia} de l'octava de Pasqua", 2, 'WHITE', 'Octava de Pasqua', 'octava')
        if dw == 6:
            nom = f"Diumenge {ROM[k]} de Pasqua" + (' (de la Divina Misericòrdia)' if k == 2 else '')
            return ('Pasqua', nom, 2, 'WHITE', f"{k}a setmana de Pasqua", 'diumenge')
        return ('Pasqua', f"{dia} de la {k}a setmana de Pasqua", 13, 'WHITE', f"{k}a setmana de Pasqua", 'feria')
    diu = d - td((dw + 1) % 7)
    k = 34 - (rei - diu).days // 7
    setm = f"{k}a setmana de durant l'any"
    if d == pent + td(7):
        return (DA, 'La Santíssima Trinitat', 3, 'WHITE', setm, 'solemnitat')
    if d == pent + td(14):
        return (DA, 'El Santíssim Cos i Sang de Crist', 3, 'WHITE', setm, 'solemnitat')
    if d == pent + td(19):
        return (DA, 'El Sagrat Cor de Jesús', 3, 'WHITE', setm, 'solemnitat')
    if d == rei:
        return (DA, "Jesucrist, Rei de l'Univers (Diumenge XXXIV de durant l'any)", 3, 'WHITE', setm, 'solemnitat')
    if dw == 6:
        return (DA, f"Diumenge {ROM[k]} de durant l'any", 6, 'GREEN', setm, 'diumenge')
    return (DA, f"{dia} de la {k}a setmana de durant l'any", 13, 'GREEN', setm, 'feria')


# ------------------------------------------------------------------ santoral
S, F, M, ML, COM, TEMP = 'SOLEMNITY', 'FEAST', 'MEMORIAL', 'OPTIONAL_MEMORIAL', 'COMMEMORATION', 'TEMPORES'
RANK_PREC = {S: 3, F: 7, M: 10, ML: 12}
FESTES_SENYOR = {'presentation_of_the_lord', 'transfiguration_of_the_lord', 'exaltation_of_the_holy_cross',
                 'dedication_of_the_lateran_basilica'}
# Celebracions de romcal que el propi de Catalunya substitueix (amb un altre grau o data).
TREURE = {'george_of_lydda_martyr', 'raymond_of_penyafort_priest', 'isidore_of_seville_bishop',
          'agnes_of_rome_virgin', 'philip_neri_priest', 'faustina_kowalska_virgin',
          'fructuosus_of_tarragona_bishop_and_augurius_of_tarragona_and_eulogius_of_tarragona_deacons_martyrs'}
GRAU_PROPI = {'solemnitat': (S, 4), 'festa': (F, 8), 'memoria': (M, 11), 'memoria-lliure': (ML, 12),
              'tempores': (TEMP, 12.5)}
COLOR_EN = {'blanc': 'WHITE', 'vermell': 'RED', 'morat': 'PURPLE', 'verd': 'GREEN', None: None}

RANG_CA = {S: 'Solemnitat', F: 'Festa', M: 'Memòria obligatòria', ML: 'Memòria lliure',
           COM: 'Commemoració', TEMP: "Témpores (celebració pròpia d'Espanya)"}
SIGLA = {S: 'S', F: 'F', M: 'M', ML: 'ml', COM: 'comm.', TEMP: ''}
COLOR_CA = {'WHITE': 'blanc', 'GREEN': 'verd', 'RED': 'vermell', 'PURPLE': 'morat', 'ROSE': 'rosat (o morat)'}
EMOJI = {'WHITE': '⚪', 'GREEN': '🟢', 'RED': '🔴', 'PURPLE': '🟣', 'ROSE': '🌸'}
CICLE = {'YEAR_A': 'A', 'YEAR_B': 'B', 'YEAR_C': 'C', 'YEAR_1': 'I (anys senars)', 'YEAR_2': 'II (anys parells)'}
SALT = {'WEEK_1': 'I', 'WEEK_2': 'II', 'WEEK_3': 'III', 'WEEK_4': 'IV'}
GRAU_TEMPS = {'diumenge': 'Diumenge', 'solemnitat': 'Solemnitat', 'festa': 'Festa', 'feria': 'Fèria',
              'feria-priv': 'Fèria privilegiada', 'octava': 'Octava de Pasqua', 'tridu': 'Tridu Pasqual'}


def genera(raw, anys, propi):
    """raw: sortida de romcal_dump.mjs; anys: anys litúrgics (any final) consecutius;
    propi: llista de dades/propi.yaml. Retorna (dies, trams, avisos)."""
    INICI, FI = advent1(anys[0] - 1), advent1(anys[-1]) - td(1)
    avisos = []
    per_dia = collections.defaultdict(list)
    info_dia = {}
    occ = collections.defaultdict(set)
    meta = {}

    def entrada(x, font='romcal'):
        k = x['id']
        if k not in NOMS:
            avisos.append(f"Falta el nom en català de «{k}»: es deixa l'identificador.")
        return dict(id=k, nom=NOMS.get(k, k.replace('_', ' ')), rank=x['rank'],
                    prec=5 if k in FESTES_SENYOR else RANK_PREC[x['rank']],
                    color=(x['colors'] or ['WHITE'])[0], font=font)

    for x in raw:
        dd = D.fromisoformat(x['date'])
        info_dia.setdefault(dd, x)
        if x['fromCal'] == 'ProperOfTime':
            continue
        occ[x['id']].add(dd)
        meta[x['id']] = x
        if x['id'] not in TREURE:
            per_dia[dd].append(entrada(x))

    def afegeix(dd, ent):
        p = ent['prec']; pt = propi_del_temps(dd)
        cur = min([pt[2]] + [e['prec'] for e in per_dia[dd] if e['rank'] in (S, F, M)])
        r = ent['rank']
        if r == S:
            if p < cur:
                per_dia[dd] = [ent]
                return
            n = dd + td(1)
            while min([propi_del_temps(n)[2]] + [e['prec'] for e in per_dia[n] if e['rank'] in (S, F)]) <= 8:
                n += td(1)
            per_dia[n] = [dict(ent, nota=f"Traslladada del {dd.day}/{dd.month} perquè aquell dia coincidia amb «{pt[1]}».")]
            avisos.append(f"{ent['nom']}: traslladada del {dd} al {n}.")
        elif r == F:
            if p < cur:
                per_dia[dd] = [ent]
        elif r == M:
            if cur <= 8:
                return
            if cur == 9:
                per_dia[dd].append(dict(ent, rank=COM))
            else:
                per_dia[dd] = [e for e in per_dia[dd] if e['rank'] != ML] + [ent]
        elif r == ML:
            if cur <= 8 or cur in (10, 11):
                return
            per_dia[dd].append(dict(ent, rank=COM) if cur == 9 else ent)
        elif r == TEMP:
            if cur > 11:
                per_dia[dd] = [e for e in per_dia[dd] if e['rank'] != ML] + [ent]

    # Reparacions de romcal: (1) posa l'Ascensió i el Corpus en dijous i hi suprimeix el santoral,
    # però a Espanya aquestes solemnitats van en diumenge; (2) alguna solemnitat de data fixa
    # pot quedar omesa (p. ex. sant Joan Baptista el 2028).
    MOBILS = {'mary_mother_of_the_church', 'immaculate_heart_of_mary',
              'our_lord_jesus_christ_the_eternal_high_priest'}
    canon = {k: collections.Counter((o.month, o.day) for o in v).most_common(1)[0][0]
             for k, v in occ.items() if k not in MOBILS}
    canon['annunciation_of_the_lord'] = (3, 25)
    reparar = []
    for y in anys:
        P = pasqua(y)
        for dj in (P + td(39), P + td(60)):
            for k, (m, dia) in canon.items():
                if (dj.month, dj.day) == (m, dia) and dj not in occ[k] and k not in TREURE:
                    reparar.append((dj, k))
    for any_civil in range(INICI.year, FI.year + 1):
        for k, (m, dia) in canon.items():
            if meta[k]['rank'] != S or k == 'annunciation_of_the_lord':
                continue
            try:
                dd = D(any_civil, m, dia)
            except ValueError:
                continue
            if INICI <= dd <= FI and not any(abs((o - dd).days) <= 21 for o in occ[k]):
                reparar.append((dd, k))
    reparar.sort(key=lambda t: RANK_PREC[meta[t[1]]['rank']])
    for dd, k in reparar:
        afegeix(dd, entrada(meta[k], 'romcal (restituït)'))

    # Propi de Catalunya i de la diòcesi
    propi_per_data = collections.defaultdict(list)
    for i, p in enumerate(propi):
        r, prec = GRAU_PROPI[p['grau']]
        propi_per_data[tuple(map(int, str(p['data']).split('-')))].append(
            dict(id=f'propi_{i}', nom=p['nom'], rank=r, prec=prec, color=COLOR_EN[p.get('color')], font='propi'))
    d = INICI
    while d <= FI:
        for ent in propi_per_data.get((d.month, d.day), []):
            afegeix(d, dict(ent))
        d += td(1)

    # A Quaresma, del 17 al 24 de desembre i a l'octava de Nadal les memòries són commemoracions
    for dd, ents in per_dia.items():
        if INICI <= dd <= FI and propi_del_temps(dd)[2] == 9:
            for e in ents:
                if e['rank'] in (M, ML):
                    e['rank'] = COM

    # ---- un registre per dia
    dies = []
    d = INICI
    while d <= FI:
        temps, nomt, pt_prec, pt_col, setm, tipus = propi_del_temps(d)
        ents = per_dia[d]
        mems = [e for e in ents if e['rank'] == M]
        if len(mems) > 1 and not [e for e in ents if e['rank'] in (S, F)]:
            for e in mems:
                e['rank'] = ML
        princ = sorted([e for e in ents if e['rank'] in (S, F, M, TEMP) and e['prec'] < pt_prec],
                       key=lambda e: e['prec'])
        opc = [e for e in ents if e['rank'] in (ML, COM)]
        info = info_dia[d]
        if princ:
            p = princ[0]
            titol = p['nom'] + (f" ({SIGLA[p['rank']]})" if SIGLA[p['rank']] else '')
            color = p['color'] or pt_col
            grau = RANG_CA[p['rank']]
            if p['id'] == 'commemoration_of_all_the_faithful_departed':
                titol, grau = p['nom'], 'Commemoració (amb precedència de solemnitat)'
        else:
            p, titol, color = None, nomt, pt_col
            grau = GRAU_TEMPS[tipus]
            if opc:
                curt = (lambda n: n.split(', ')[0]) if len(opc) > 1 else (lambda n: n)
                titol += ' · ' + ' / '.join(curt(o['nom']) + f" ({SIGLA[o['rank']]})" for o in opc)
        desc = []
        if p:
            desc.append(f"Dia litúrgic: {nomt}")
        desc.append(f"Temps litúrgic: {temps} — {setm}")
        desc.append(f"Celebració: {p['nom'] if p else nomt} — {grau}")
        desc += [f"{RANG_CA[o['rank']]}: {o['nom']}" for o in opc]
        if p and p.get('nota'):
            desc.append(p['nota'])
        desc.append(f"Color litúrgic: {COLOR_CA[color]}")
        desc.append(f"Salteri: setmana {SALT.get(info['psalter'], '—')}")
        desc.append(f"Cicle dominical: {CICLE[info['sunCycle']]} · Cicle ferial: {CICLE[info['wkCycle']]}")
        dies.append(dict(data=d, titol=f"{EMOJI[color]} {titol}", desc='\n'.join(desc)))
        d += td(1)

    # ---- franges dels temps litúrgics i inici de cada any
    trams = []
    idx = {x['data']: x for x in dies}
    for y in anys:
        A1 = advent1(y - 1); P = pasqua(y); bapt = baptisme(y)
        cendra = P - td(46); pent = P + td(49)
        info = info_dia[A1]
        curs = f"{y - 1}-{str(y)[2:]}"
        cic = f"cicle dominical {CICLE[info['sunCycle']]}, cicle ferial {CICLE[info['wkCycle']].split(' ')[0]}"
        idx[A1]['desc'] = f"Inici de l'any litúrgic {curs} ({cic}).\n" + idx[A1]['desc']
        for nom, a, b in [
            ("🟣 Temps d'Advent", A1, D(y - 1, 12, 24)),
            ("⚪ Temps de Nadal", D(y - 1, 12, 25), bapt),
            ("🟢 Temps de durant l'any (1a part)", bapt + td(1), cendra - td(1)),
            ("🟣 Temps de Quaresma", cendra, P - td(3)),
            ("⚪ Tridu Pasqual", P - td(3), P),
            ("⚪ Temps de Pasqua", P, pent),
            ("🟢 Temps de durant l'any (2a part)", pent + td(1), advent1(y) - td(1)),
        ]:
            trams.append(dict(nom=f"{nom} · curs {curs} ({cic})", ini=a, fi=b))
    return dies, trams, avisos
