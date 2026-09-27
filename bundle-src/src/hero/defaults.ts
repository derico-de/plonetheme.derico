/**
 * What a freshly inserted hero already says.
 *
 * Aurora's slash menu inserts a node with only `@type` and `blocksConfig` has
 * no initial-data hook, so `HeroEdit` seeds it with the mockup's copy: the
 * author edits fields instead of inventing them.
 *
 * This is text, not template: every word here is stored on the block and
 * every word is editable. It is a starting draft, not a fallback — the
 * renderers still omit whatever is absent (`data.ts`), and an author who
 * clears the headline gets a hero with no headline, not this one back.
 *
 * Copy is the German homepage from the design mockup,
 * `docs/design/derico.de/site/de/index.html`. German because that is the
 * mockup's primary language and the site's; the block has no i18n surface of
 * its own — the seed is content, and content gets translated by editing it.
 *
 * Deliberately NOT seeded: `cta_href`, `link_href`, `image_wide`,
 * `image_portrait`. Those are references into one particular site's content,
 * and a plausible-looking path that resolves nowhere is worse than an empty
 * field — the canvas nag names each of them until it is picked
 * (`HeroEdit.missing`).
 */
import type { HeroData } from './data';

/** The keys the hero owns — everything `HeroSchema` lets an author write. */
export const HERO_FIELDS = [
  'kicker',
  'headline',
  'lede',
  'cta_label',
  'cta_href',
  'link_label',
  'link_href',
  'image_wide',
  'image_portrait',
  'legend',
] as const;

export const HERO_DEFAULTS: HeroData = {
  kicker: 'Nachhaltige Lösungen, seit über 20 Jahren',
  headline: 'Anwendungen, die bleiben.',
  lede:
    'Wir entwickeln Geschäftsanwendungen auf Basis von Python, modernem ' +
    'JavaScript und Open Source. Wartbarkeit, offene Standards und klare ' +
    'Entscheidungen sichern ihren Wert über viele Jahre.',
  cta_label: 'Erstgespräch vereinbaren',
  link_label: 'Alle Leistungen',
  legend: [
    { title: 'schneller Prototyp', subtitle: 'in Wochen bedienbar' },
    { title: 'erste Anwendung', subtitle: 'trägt die tägliche Arbeit' },
    { title: 'erfahrener Begleiter', subtitle: 'wächst mit den Anforderungen' },
    { title: 'mit der Zeit gegangen', subtitle: 'offen, aktuell, migrierbar' },
  ],
};

/**
 * Has this block been through the seeding yet?
 *
 * Asked of the KEYS, never of their values. An author who empties the
 * headline leaves `headline: ''` behind, and a check for "no text anywhere"
 * would read that as a fresh insert and hand the mockup's headline straight
 * back — which is the one behaviour that would make the seed feel like a
 * fallback the author cannot get out from under. A node that has never met
 * this code carries `@type` and the materialised `blockWidth` and no hero key
 * at all.
 */
export function unseeded(data: HeroData): boolean {
  return !HERO_FIELDS.some((field) => field in data);
}

/**
 * The block data a fresh insert should carry.
 *
 * A merge, not a replacement: whatever the host already put on the node —
 * `@type`, the materialised `blockWidth`, anything a future
 * plugin adds — survives untouched.
 */
export function seeded(data: HeroData): HeroData {
  return { ...data, ...HERO_DEFAULTS };
}

export default HERO_DEFAULTS;
