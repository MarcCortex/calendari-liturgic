"""Calendari litúrgic en català: propi del temps (calculat aquí) + santoral (romcal, Espanya)
+ propi de Catalunya i de la diòcesi (dades/propi.yaml)."""
import collections
import urllib.parse
import datetime as dt

from noms_ca import NOMS, NOMS_ES

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


DIES = {'ca': ['Dilluns', 'Dimarts', 'Dimecres', 'Dijous', 'Divendres', 'Dissabte', 'Diumenge'],
        'es': ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']}
ROM = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII', 'XIV', 'XV',
       'XVI', 'XVII', 'XVIII', 'XIX', 'XX', 'XXI', 'XXII', 'XXIII', 'XXIV', 'XXV', 'XXVI', 'XXVII',
       'XXVIII', 'XXIX', 'XXX', 'XXXI', 'XXXII', 'XXXIII', 'XXXIV']
ORD_DIA = {'ca': {26: '2n', 27: '3r', 28: '4t', 29: '5è', 30: '6è', 31: '7è'},
           'es': {26: '2.º', 27: '3.º', 28: '4.º', 29: '5.º', 30: '6.º', 31: '7.º'}}

# Textos del propi del temps. {k}: número de setmana; {r}: número romà; {dia}: dia de la setmana; {n}: dia del mes
T = {
 'ca': dict(
    advent='Advent', nadal='Nadal', da="Durant l'any", quaresma='Quaresma', tridu='Tridu Pasqual', pasqua='Pasqua',
    s_advent="Setmana {r} d'Advent", s_da="Setmana {r} de durant l'any", s_quaresma="Setmana {r} de Quaresma",
    s_pasqua="Setmana {r} de Pasqua", oct_nadal='Octava de Nadal', t_nadal='Temps de Nadal',
    inici_quaresma='Inici de la Quaresma', setmana_santa='Setmana Santa', oct_pasqua='Octava de Pasqua',
    cloenda_pasqua='Cloenda del temps de Pasqua',
    diu_advent="Diumenge {r} d'Advent", gaudete=' (Gaudete)', feria_priv="Fèria privilegiada d'Advent ({n} de desembre)",
    feria_advent="{dia} de la setmana {r} d'Advent",
    nadal_dia='La Nativitat del Senyor (Nadal)', mare_deu='Santa Maria, Mare de Déu (Octava de Nadal)',
    epifania="L'Epifania del Senyor", baptisme='El Baptisme del Senyor',
    sagrada_familia='La Sagrada Família de Jesús, Maria i Josep', octava_nadal="{o} dia de l'octava de Nadal",
    diu2_nadal='Diumenge II després de Nadal', feria_gener='Fèria del temps de Nadal ({n} de gener)',
    post_epifania="{dia} després de l'Epifania",
    diu_da="Diumenge {r} de durant l'any", paraula=' · Diumenge de la Paraula de Déu',
    feria_da="{dia} de la setmana {r} de durant l'any",
    cendra='Dimecres de Cendra', post_cendra='{dia} després de Cendra', rams='Diumenge de Rams de la Passió del Senyor',
    set_santa='{dia} Sant', diu_quaresma='Diumenge {r} de Quaresma', laetare=' (Laetare)',
    feria_quaresma='{dia} de la setmana {r} de Quaresma',
    dijous_sant='Dijous Sant · Missa vespertina de la Cena del Senyor (inici del Tridu Pasqual)',
    divendres_sant='Divendres Sant de la Passió del Senyor', dissabte_sant='Dissabte Sant · Vetlla Pasqual',
    diu_pasqua='Diumenge de Pasqua de la Resurrecció del Senyor', pentecosta='Diumenge de Pentecosta',
    ascensio="L'Ascensió del Senyor (Diumenge VII de Pasqua)", octava_pasqua="{dia} de l'octava de Pasqua",
    diu_pasqua_n='Diumenge {r} de Pasqua', misericordia=' (de la Divina Misericòrdia)',
    feria_pasqua='{dia} de la setmana {r} de Pasqua',
    trinitat='La Santíssima Trinitat', corpus='El Santíssim Cos i Sang de Crist', sagrat_cor='El Sagrat Cor de Jesús',
    crist_rei="Jesucrist, Rei de l'Univers (Diumenge XXXIV de durant l'any)"),
 'es': dict(
    advent='Adviento', nadal='Navidad', da='Tiempo Ordinario', quaresma='Cuaresma', tridu='Triduo Pascual', pasqua='Pascua',
    s_advent='Semana {r} de Adviento', s_da='Semana {r} del Tiempo Ordinario', s_quaresma='Semana {r} de Cuaresma',
    s_pasqua='Semana {r} de Pascua', oct_nadal='Octava de Navidad', t_nadal='Tiempo de Navidad',
    inici_quaresma='Inicio de la Cuaresma', setmana_santa='Semana Santa', oct_pasqua='Octava de Pascua',
    cloenda_pasqua='Final del tiempo de Pascua',
    diu_advent='Domingo {r} de Adviento', gaudete=' (Gaudete)', feria_priv='Feria privilegiada de Adviento ({n} de diciembre)',
    feria_advent='{dia} de la semana {r} de Adviento',
    nadal_dia='La Natividad del Señor (Navidad)', mare_deu='Santa María, Madre de Dios (Octava de Navidad)',
    epifania='La Epifanía del Señor', baptisme='El Bautismo del Señor',
    sagrada_familia='La Sagrada Familia de Jesús, María y José', octava_nadal='{o} día de la octava de Navidad',
    diu2_nadal='Domingo II después de Navidad', feria_gener='Feria del tiempo de Navidad ({n} de enero)',
    post_epifania='{dia} después de la Epifanía',
    diu_da='Domingo {r} del Tiempo Ordinario', paraula=' · Domingo de la Palabra de Dios',
    feria_da='{dia} de la semana {r} del Tiempo Ordinario',
    cendra='Miércoles de Ceniza', post_cendra='{dia} después de Ceniza', rams='Domingo de Ramos en la Pasión del Señor',
    set_santa='{dia} Santo', diu_quaresma='Domingo {r} de Cuaresma', laetare=' (Laetare)',
    feria_quaresma='{dia} de la semana {r} de Cuaresma',
    dijous_sant='Jueves Santo · Misa vespertina de la Cena del Señor (inicio del Triduo Pascual)',
    divendres_sant='Viernes Santo de la Pasión del Señor', dissabte_sant='Sábado Santo · Vigilia Pascual',
    diu_pasqua='Domingo de Pascua de la Resurrección del Señor', pentecosta='Domingo de Pentecostés',
    ascensio='La Ascensión del Señor (Domingo VII de Pascua)', octava_pasqua='{dia} de la octava de Pascua',
    diu_pasqua_n='Domingo {r} de Pascua', misericordia=' (de la Divina Misericordia)',
    feria_pasqua='{dia} de la semana {r} de Pascua',
    trinitat='La Santísima Trinidad', corpus='El Santísimo Cuerpo y Sangre de Cristo', sagrat_cor='El Sagrado Corazón de Jesús',
    crist_rei='Jesucristo, Rey del Universo (Domingo XXXIV del Tiempo Ordinario)'),
}


def propi_del_temps(d, lang='ca'):
    """(temps, nom, precedència, color, setmana, tipus). Precedència segons la taula de les
    Normes universals: 1 Tridu; 2 Nadal, Epifania, Ascensió, Pentecosta, diumenges d'Advent,
    Quaresma i Pasqua, Cendra, Setmana Santa, octava de Pasqua; 3 solemnitats; 5 festes del Senyor;
    6 diumenges de Nadal i de durant l'any; 9 fèries privilegiades; 13 fèries."""
    t = T[lang]
    y = any_liturgic(d)
    A1 = advent1(y - 1); nadal = D(y - 1, 12, 25); ep = D(y, 1, 6); bapt = baptisme(y)
    P = pasqua(y); cendra = P - td(46); pent = P + td(49); rei = advent1(y) - td(7)
    dw = d.weekday(); dia = DIES[lang][dw]

    if A1 <= d < nadal:
        k = (d - A1).days // 7 + 1
        setm = t['s_advent'].format(k=k, r=ROM[k])
        if dw == 6:
            nom = t['diu_advent'].format(r=ROM[k]) + (t['gaudete'] if k == 3 else '')
            return (t['advent'], nom, 2, 'ROSE' if k == 3 else 'PURPLE', setm, 'diumenge')
        if d.month == 12 and d.day >= 17:
            return (t['advent'], t['feria_priv'].format(n=d.day), 9, 'PURPLE', setm, 'feria')
        return (t['advent'], t['feria_advent'].format(dia=dia, k=k, r=ROM[k]), 13, 'PURPLE', setm, 'feria')
    if nadal <= d <= bapt:
        if d == nadal:
            return (t['nadal'], t['nadal_dia'], 2, 'WHITE', t['oct_nadal'], 'solemnitat')
        if d == D(y, 1, 1):
            return (t['nadal'], t['mare_deu'], 3, 'WHITE', t['oct_nadal'], 'solemnitat')
        if d == ep:
            return (t['nadal'], t['epifania'], 2, 'WHITE', t['t_nadal'], 'solemnitat')
        if d == bapt:
            return (t['nadal'], t['baptisme'], 5, 'WHITE', t['t_nadal'], 'festa')
        sf = next((nadal + td(i) for i in range(1, 7) if (nadal + td(i)).weekday() == 6), D(y - 1, 12, 30))
        if d == sf:
            return (t['nadal'], t['sagrada_familia'], 5, 'WHITE', t['oct_nadal'], 'festa')
        if d.month == 12:
            return (t['nadal'], t['octava_nadal'].format(o=ORD_DIA[lang][d.day]), 9, 'WHITE', t['oct_nadal'], 'feria')
        if d < ep:
            if dw == 6:
                return (t['nadal'], t['diu2_nadal'], 6, 'WHITE', t['t_nadal'], 'diumenge')
            return (t['nadal'], t['feria_gener'].format(n=d.day), 13, 'WHITE', t['t_nadal'], 'feria')
        return (t['nadal'], t['post_epifania'].format(dia=dia), 13, 'WHITE', t['t_nadal'], 'feria')
    if bapt < d < cendra:
        k = (d - bapt).days // 7 + 1
        setm = t['s_da'].format(k=k, r=ROM[k])
        if dw == 6:
            nom = t['diu_da'].format(r=ROM[k]) + (t['paraula'] if k == 3 else '')
            return (t['da'], nom, 6, 'GREEN', setm, 'diumenge')
        return (t['da'], t['feria_da'].format(dia=dia, k=k, r=ROM[k]), 13, 'GREEN', setm, 'feria')
    if cendra <= d < P - td(3):
        if d == cendra:
            return (t['quaresma'], t['cendra'], 2, 'PURPLE', t['inici_quaresma'], 'feria-priv')
        if d < cendra + td(4):
            return (t['quaresma'], t['post_cendra'].format(dia=dia), 9, 'PURPLE', t['inici_quaresma'], 'feria')
        k = (d - (cendra + td(4))).days // 7 + 1
        if k == 6:
            if dw == 6:
                return (t['quaresma'], t['rams'], 2, 'RED', t['setmana_santa'], 'diumenge')
            return (t['quaresma'], t['set_santa'].format(dia=dia), 2, 'PURPLE', t['setmana_santa'], 'feria-priv')
        setm = t['s_quaresma'].format(k=k, r=ROM[k])
        if dw == 6:
            nom = t['diu_quaresma'].format(r=ROM[k]) + (t['laetare'] if k == 4 else '')
            return (t['quaresma'], nom, 2, 'ROSE' if k == 4 else 'PURPLE', setm, 'diumenge')
        return (t['quaresma'], t['feria_quaresma'].format(dia=dia, k=k, r=ROM[k]), 9, 'PURPLE', setm, 'feria')
    if P - td(3) <= d <= P:
        noms = {3: (t['dijous_sant'], 'WHITE'), 2: (t['divendres_sant'], 'RED'),
                1: (t['dissabte_sant'], 'WHITE'), 0: (t['diu_pasqua'], 'WHITE')}
        n, c = noms[(P - d).days]
        if d == P:
            return (t['pasqua'], n, 1, c, t['oct_pasqua'], 'solemnitat')
        return (t['tridu'], n, 1, c, t['tridu'], 'tridu')
    if P < d <= pent:
        k = (d - P).days // 7 + 1
        if d == pent:
            return (t['pasqua'], t['pentecosta'], 2, 'RED', t['cloenda_pasqua'], 'solemnitat')
        if d == P + td(42):
            return (t['pasqua'], t['ascensio'], 2, 'WHITE', t['s_pasqua'].format(k=7, r='VII'), 'solemnitat')
        if k == 1:
            return (t['pasqua'], t['octava_pasqua'].format(dia=dia), 2, 'WHITE', t['oct_pasqua'], 'octava')
        setm = t['s_pasqua'].format(k=k, r=ROM[k])
        if dw == 6:
            nom = t['diu_pasqua_n'].format(r=ROM[k]) + (t['misericordia'] if k == 2 else '')
            return (t['pasqua'], nom, 2, 'WHITE', setm, 'diumenge')
        return (t['pasqua'], t['feria_pasqua'].format(dia=dia, k=k, r=ROM[k]), 13, 'WHITE', setm, 'feria')
    diu = d - td((dw + 1) % 7)
    k = 34 - (rei - diu).days // 7
    setm = t['s_da'].format(k=k, r=ROM[k])
    if d == pent + td(7):
        return (t['da'], t['trinitat'], 3, 'WHITE', setm, 'solemnitat')
    if d == pent + td(14):
        return (t['da'], t['corpus'], 3, 'WHITE', setm, 'solemnitat')
    if d == pent + td(19):
        return (t['da'], t['sagrat_cor'], 3, 'WHITE', setm, 'solemnitat')
    if d == rei:
        return (t['da'], t['crist_rei'], 3, 'WHITE', setm, 'solemnitat')
    if dw == 6:
        return (t['da'], t['diu_da'].format(r=ROM[k]), 6, 'GREEN', setm, 'diumenge')
    return (t['da'], t['feria_da'].format(dia=dia, k=k, r=ROM[k]), 13, 'GREEN', setm, 'feria')


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

SIGLA = {S: 'S', F: 'F', M: 'M', ML: 'ml', COM: 'comm.', TEMP: ''}
EMOJI = {'WHITE': '⚪', 'GREEN': '🟢', 'RED': '🔴', 'PURPLE': '🟣', 'ROSE': '🌸'}
SALT = {'WEEK_1': 'I', 'WEEK_2': 'II', 'WEEK_3': 'III', 'WEEK_4': 'IV'}
# Etiquetes de la descripció, en cada llengua
E = {
 'ca': dict(
    rang={S: 'Solemnitat', F: 'Festa', M: 'Memòria obligatòria', ML: 'Memòria lliure',
          COM: 'Commemoració', TEMP: "Témpores (celebració pròpia d'Espanya)"},
    color={'WHITE': 'blanc', 'GREEN': 'verd', 'RED': 'vermell', 'PURPLE': 'morat', 'ROSE': 'rosat (o morat)'},
    cicle={'YEAR_A': 'A', 'YEAR_B': 'B', 'YEAR_C': 'C', 'YEAR_1': 'I (anys senars)', 'YEAR_2': 'II (anys parells)'},
    grau_temps={'diumenge': 'Diumenge', 'solemnitat': 'Solemnitat', 'festa': 'Festa', 'feria': 'Fèria',
                'feria-priv': 'Fèria privilegiada', 'octava': 'Octava de Pasqua', 'tridu': 'Tridu Pasqual'},
    difunts='Commemoració (amb precedència de solemnitat)', i=' i ',
    dia='Dia litúrgic', temps='Temps litúrgic', celebracio='Celebració', color_l='Color litúrgic',
    salteri='Salteri: setmana', cicle_dom='Cicle dominical', cicle_fer='Cicle ferial',
    trasllat="Traslladada del {d}/{m} perquè aquell dia coincidia amb «{nom}».",
    inici_any="Inici de l'any litúrgic {curs} ({cic}).", cic="cicle dominical {a}, cicle ferial {b}",
    curs='curs', trams=["Temps d'Advent", 'Temps de Nadal', "Temps de durant l'any (1a part)", 'Temps de Quaresma',
                        'Tridu Pasqual', 'Temps de Pasqua', "Temps de durant l'any (2a part)"],
    del_al='Del {a} al {b}.', mes_info='Més informació (Viquipèdia):',
    wiki='https://ca.wikipedia.org/w/index.php?title=Especial:Cerca&go=V%C3%A9s&search='),
 'es': dict(
    rang={S: 'Solemnidad', F: 'Fiesta', M: 'Memoria obligatoria', ML: 'Memoria libre',
          COM: 'Conmemoración', TEMP: 'Témporas (celebración propia de España)'},
    color={'WHITE': 'blanco', 'GREEN': 'verde', 'RED': 'rojo', 'PURPLE': 'morado', 'ROSE': 'rosa (o morado)'},
    cicle={'YEAR_A': 'A', 'YEAR_B': 'B', 'YEAR_C': 'C', 'YEAR_1': 'I (años impares)', 'YEAR_2': 'II (años pares)'},
    grau_temps={'diumenge': 'Domingo', 'solemnitat': 'Solemnidad', 'festa': 'Fiesta', 'feria': 'Feria',
                'feria-priv': 'Feria privilegiada', 'octava': 'Octava de Pascua', 'tridu': 'Triduo Pascual'},
    difunts='Conmemoración (con precedencia de solemnidad)', i=' y ',
    dia='Día litúrgico', temps='Tiempo litúrgico', celebracio='Celebración', color_l='Color litúrgico',
    salteri='Salterio: semana', cicle_dom='Ciclo dominical', cicle_fer='Ciclo ferial',
    trasllat='Trasladada del {d}/{m} porque ese día coincidía con «{nom}».',
    inici_any='Inicio del año litúrgico {curs} ({cic}).', cic='ciclo dominical {a}, ciclo ferial {b}',
    curs='curso', trams=['Tiempo de Adviento', 'Tiempo de Navidad', 'Tiempo Ordinario (1.ª parte)', 'Tiempo de Cuaresma',
                         'Triduo Pascual', 'Tiempo de Pascua', 'Tiempo Ordinario (2.ª parte)'],
    del_al='Del {a} al {b}.', mes_info='Más información (Wikipedia):',
    wiki='https://es.wikipedia.org/w/index.php?title=Especial:Buscar&go=Ir&search='),
}


def enllac_wiki(nom, L):
    """Enllaç de cerca a la Viquipèdia: obre l'article si el títol coincideix; si no, la llista de resultats."""
    return L['wiki'] + urllib.parse.quote_plus(nom.split(', ')[0])


def genera(raw, anys, propi, emojis=False, sigles=False, lang='ca'):
    """raw: sortida de romcal_dump.mjs; anys: anys litúrgics (any final) consecutius;
    propi: llista de dades/propi.yaml. Retorna (dies, trams, avisos)."""
    INICI, FI = advent1(anys[0] - 1), advent1(anys[-1]) - td(1)
    L = E[lang]
    pdt = lambda dd: propi_del_temps(dd, lang)  # noqa: E731
    avisos = []
    per_dia = collections.defaultdict(list)
    info_dia = {}
    occ = collections.defaultdict(set)
    meta = {}

    def entrada(x, font='romcal'):
        k = x['id']
        if lang == 'ca' and k not in NOMS:
            avisos.append(f"Falta el nom en català de «{k}»: es deixa l'identificador.")
        nom = NOMS.get(k, k.replace('_', ' ')) if lang == 'ca' else NOMS_ES.get(k, x.get('name') or k)
        return dict(id=k, nom=nom, rank=x['rank'],
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
        p = ent['prec']; pt = pdt(dd)
        cur = min([pt[2]] + [e['prec'] for e in per_dia[dd] if e['rank'] in (S, F, M)])
        r = ent['rank']
        if r == S:
            if p < cur:
                per_dia[dd] = [ent]
                return
            n = dd + td(1)
            while min([pdt(n)[2]] + [e['prec'] for e in per_dia[n] if e['rank'] in (S, F)]) <= 8:
                n += td(1)
            per_dia[n] = [dict(ent, nota=L['trasllat'].format(d=dd.day, m=dd.month, nom=pt[1]))]
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
            dict(id=f'propi_{i}', nom=(p.get('nom_es') or p['nom']) if lang == 'es' else p['nom'], rank=r, prec=prec, color=COLOR_EN[p.get('color')], font='propi'))
    d = INICI
    while d <= FI:
        for ent in propi_per_data.get((d.month, d.day), []):
            afegeix(d, dict(ent))
        d += td(1)

    # A Quaresma, del 17 al 24 de desembre i a l'octava de Nadal les memòries són commemoracions
    for dd, ents in per_dia.items():
        if INICI <= dd <= FI and pdt(dd)[2] == 9:
            for e in ents:
                if e['rank'] in (M, ML):
                    e['rank'] = COM

    # ---- un registre per dia
    dies = []
    d = INICI
    while d <= FI:
        temps, nomt, pt_prec, pt_col, setm, tipus = pdt(d)
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
            titol = p['nom'] + (f" ({SIGLA[p['rank']]})" if sigles and SIGLA[p['rank']] else '')
            color = p['color'] or pt_col
            grau = L['rang'][p['rank']]
            if p['id'] == 'commemoration_of_all_the_faithful_departed':
                titol, grau = p['nom'], L['difunts']
        else:
            p, titol, color = None, nomt, pt_col
            grau = L['grau_temps'][tipus]
            # Fèria amb memòries lliures: el títol és només el nom dels sants.
            # (A Quaresma i en les fèries privilegiades es manté el nom del dia.)
            lliures = opc  # memòries lliures o commemoracions (Quaresma, 17-31 de desembre)
            if lliures:
                noms = [o['nom'].split(', ')[0] + (f" ({SIGLA[o['rank']]})" if sigles else '') for o in lliures]
                titol = noms[0] if len(noms) == 1 else ', '.join(noms[:-1]) + L['i'] + noms[-1]
        desc = []
        if p:
            desc.append(f"{L['dia']}: {nomt}")
        desc.append(f"{L['temps']}: {temps} — {setm}")
        desc.append(f"{L['celebracio']}: {p['nom'] if p else nomt} — {grau}")
        desc += [f"{L['rang'][o['rank']]}: {o['nom']}" for o in opc]
        if p and p.get('nota'):
            desc.append(p['nota'])
        desc.append(f"{L['color_l']}: {L['color'][color]}")
        desc.append(f"{L['salteri']} {SALT.get(info['psalter'], '—')}")
        desc.append(f"{L['cicle_dom']}: {L['cicle'][info['sunCycle']]} · {L['cicle_fer']}: {L['cicle'][info['wkCycle']]}")
        sants = ([p] if p and p['rank'] != TEMP else []) + opc
        if sants:
            desc += ['', L['mes_info']]
            desc += [f"· {e['nom'].split(', ')[0]}: {enllac_wiki(e['nom'], L)}" for e in sants]
        # Dia "normal": fèria sense cap sant ni celebració. No es publica.
        buit = not princ and not opc and tipus == 'feria'
        dies.append(dict(data=d, buit=buit, titol=(f"{EMOJI[color]} " if emojis else '') + titol, desc='\n'.join(desc)))
        d += td(1)

    # ---- franges dels temps litúrgics i inici de cada any
    trams = []
    idx = {x['data']: x for x in dies}
    for y in anys:
        A1 = advent1(y - 1); P = pasqua(y); bapt = baptisme(y)
        cendra = P - td(46); pent = P + td(49)
        info = info_dia[A1]
        curs = f"{y - 1}-{str(y)[2:]}"
        cic = L['cic'].format(a=L['cicle'][info['sunCycle']], b=L['cicle'][info['wkCycle']].split(' ')[0])
        idx[A1]['desc'] = L['inici_any'].format(curs=curs, cic=cic) + '\n' + idx[A1]['desc']
        franges = [(A1, D(y - 1, 12, 24)), (D(y - 1, 12, 25), bapt), (bapt + td(1), cendra - td(1)),
                   (cendra, P - td(3)), (P - td(3), P), (P, pent), (pent + td(1), advent1(y) - td(1))]
        colors = ['🟣', '⚪', '🟢', '🟣', '⚪', '⚪', '🟢']
        for nom, col, (a, b) in zip(L['trams'], colors, franges):
            nom = f"{col} {nom}" if emojis else nom
            trams.append(dict(nom=f"{nom} · {L['curs']} {curs} ({cic})", ini=a, fi=b,
                              desc=L['del_al'].format(a=f"{a:%d/%m/%Y}", b=f"{b:%d/%m/%Y}")))
    return dies, trams, avisos
