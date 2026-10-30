# Calendari litúrgic en català

Genera i publica dos calendaris als quals et pots subscriure des de Google Calendar, Apple Calendar o Outlook:

| Fitxer | Contingut |
|---|---|
| `calendari-ca.ics` | **Català**: calendari litúrgic i dates del Camí, tot junt. |
| `calendari-es.ics` | **Castellano**: el mateix calendari en castellà. |

Cada dia amb alguna celebració (diumenges, solemnitats, festes, memòries i sants) porta el nom al títol; els dies feriers sense cap sant no surten. En obrir-lo hi ha el temps i la setmana, el grau, el color litúrgic, el salteri i els cicles. Els textos en castellà de les dates del Camí i del propi són als camps `titol_es`, `descripcio_es` i `nom_es` dels fitxers de `dades/`.

El calendari és el romà general amb el propi d'Espanya (via [romcal](https://github.com/romcal/romcal)), més el propi de Catalunya i de la diòcesi de Sant Feliu de Llobregat (`dades/propi.yaml`). Cobreix l'any litúrgic en curs i els tres següents. GitHub el torna a generar sol el dia 1 de cada mes i cada vegada que es modifica algun fitxer.

## Posada en marxa (només un cop)

1. Crea un repositori **públic** a GitHub (per exemple, `calendari-liturgic`) i puja-hi aquests fitxers.
   *GitHub Pages és gratuït només per a repositoris públics. Els calendaris no contenen cap dada personal.*
2. Al repositori, ves a **Settings → Pages** i, a *Build and deployment → Source*, tria **GitHub Actions**.
3. Ves a **Actions → Publica els calendaris → Run workflow**. Al cap d'un o dos minuts la pàgina ja estarà publicada a
   `https://<el-teu-usuari>.github.io/calendari-liturgic/`
4. Obre aquesta pàgina i prem **Afegeix a Google Calendar** al calendari que vulguis.

## Afegir o canviar dates

- **Camí:** edita `dades/cami.yaml` (des de GitHub mateix, amb la icona del llapis) i prem *Commit changes*.
- **Sants propis:** edita `dades/propi.yaml`.

En un parell de minuts es publica la nova versió, i Google la recull a la propera comprovació (normalment unes quantes vegades al dia).

## Provar-ho a l'ordinador

```bash
npm ci
pip install -r requirements.txt
python generador/main.py --sortida public          # amb la data d'avui
python generador/main.py --sortida public --avui 2027-12-01   # com si fos una altra data
```

## Estructura

```
dades/cami.yaml          dates del Camí (editable)
dades/propi.yaml         propi de Catalunya i de la diòcesi (editable)
generador/main.py        punt d'entrada: decideix els anys, crida romcal i escriu els .ics
generador/liturgia.py    propi del temps, normes de precedència i trasllats
generador/cami.py        aniversaris del Camí
generador/noms_ca.py     noms dels sants en català
generador/ics.py         format iCalendar
romcal_dump.mjs          extreu el santoral d'Espanya de romcal
web/index.html           pàgina amb els enllaços de subscripció
.github/workflows/       tasca automàtica de GitHub Actions
```
