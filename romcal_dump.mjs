// Extreu de romcal (calendari d'Espanya) les dades de cada dia dels anys litúrgics demanats.
// Ús: node romcal_dump.mjs <fitxer_sortida.json> <any> [<any> ...]
// "any" és l'any en què acaba l'any litúrgic (2027 = de l'Advent del 2026 al novembre del 2027).
import { Romcal } from 'romcal';
import { Spain_Es } from '@romcal/calendar.spain';
import fs from 'fs';

const [sortida, ...anys] = process.argv.slice(2);
const out = [];
for (const y of anys.map(Number)) {
  const r = new Romcal({ localizedCalendar: Spain_Es, scope: 'liturgical' });
  const cal = await r.generateCalendar(y);
  for (const [d, evs] of Object.entries(cal)) {
    evs.forEach((e) => out.push({
      date: d, id: e.id, name: e.name, rank: e.rank, colors: e.colors,
      psalter: e.cycles?.psalterWeek, sunCycle: e.cycles?.sundayCycle, wkCycle: e.cycles?.weekdayCycle,
      fromCal: e.fromCalendarId,
    }));
  }
}
fs.writeFileSync(sortida, JSON.stringify(out));
console.log(`romcal: ${out.length} entrades (${anys.join(', ')})`);
