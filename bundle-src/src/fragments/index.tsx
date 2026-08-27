/**
 * derico's fragment corpus, published into the shared registry.
 *
 * `collective.fragmentsblock` ships a generic fragment block whose picker
 * enumerates whatever add-ons registered as `@plone/registry` utilities of
 * type `collective.fragmentsblock.fragment`. This entry makes derico the
 * first provider, over the corpus it already has: the same
 * `snippets/*.html` files the Derico Snippet block renders and
 * `fragments.py` serves — three readers, one corpus, no copies.
 *
 * The imports and the titles are restated here rather than taken from
 * `../snippet/`, and the `?raw&entry=fragments` query is load-bearing: a
 * module shared between two entries becomes a shared CHUNK, and a record
 * loads exactly ONE file, so the build guard rejects it (contract §2.1).
 * The extra query makes this a distinct module id, so each bundle carries
 * its own copy of the markup — 5 KB, against a chunk the record cannot
 * declare. `fragments.test.ts` holds this map and the Snippet block's in
 * lockstep instead, the same trade the corpus already makes between its
 * Python and TypeScript readers.
 *
 * Deliberately NOT a block: this bundle registers no `blocksConfig` entry,
 * and its record declares no `types`. The record exists only because a
 * record is how `@@aurora-edit` loads a bundle at all — the loader gates on
 * `enabled`/bundle/block-api and never on `types` (blockaddons.py:198ff).
 *
 * No dependency on the add-on's npm package (unpublished): the registry
 * call IS the contract, and `collective.fragmentsblock`'s README blesses
 * the bare form.
 */
import balkenlage from '../../../src/plonetheme/derico/snippets/balkenlage.html?raw&entry=fragments';
import serviceFrame from '../../../src/plonetheme/derico/snippets/service-frame.html?raw&entry=fragments';

/** The utility type `collective.fragmentsblock` enumerates. */
export const FRAGMENT_UTILITY_TYPE = 'collective.fragmentsblock.fragment';

type FragmentRecord = { id: string; title: string; html: string };

type FragmentRegistry = {
  registerUtility: (options: {
    type: string;
    name: string;
    method: unknown;
  }) => void;
};

/**
 * One record per shipped ornament, titled the way the Derico Snippet's own
 * picker titles it. The id is the file stem, which is also the key the
 * server resolves to `snippets/<id>.html` — the add-on's slug rule
 * (`^[A-Za-z0-9][A-Za-z0-9_-]*$`) is what the corpus filenames already are.
 */
export const DERICO_FRAGMENTS: FragmentRecord[] = [
  { id: 'balkenlage', title: 'Balkenlage (Trenner)', html: balkenlage },
  { id: 'service-frame', title: 'Ständerwerk (Rahmen)', html: serviceFrame },
];

export default function installDericoFragments<T extends FragmentRegistry>(
  config: T,
): T {
  for (const record of DERICO_FRAGMENTS) {
    config.registerUtility({
      type: FRAGMENT_UTILITY_TYPE,
      name: record.id,
      method: record,
    });
  }
  return config;
}
