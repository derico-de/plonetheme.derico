/**
 * derico's fragment corpus, published into the shared registry.
 *
 * `collective.fragmentsblock` ships a generic fragment block whose picker
 * enumerates whatever add-ons registered as `@plone/registry` utilities of
 * type `collective.fragmentsblock.fragment`. This entry makes derico the
 * only provider, over the corpus in the Python package: the same
 * `snippets/*.html` files `fragments.py` serves to classic rendering. Two
 * readers, one corpus, no copies — `fragments.test.ts` holds the map below
 * against the directory on disk, and `tests/test_fragments.py` holds it
 * against the server's view of the same files.
 *
 * Should a second entry ever import this corpus, give one of them a
 * distinct module id (`?raw&entry=…`): a module shared between two entries
 * becomes a CHUNK, and a record loads exactly one file, so the build guard
 * rejects it (contract §2.1).
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
import balkenlage from '../../../src/plonetheme/derico/snippets/balkenlage.html?raw';
import serviceFrame from '../../../src/plonetheme/derico/snippets/service-frame.html?raw';

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
 * One record per shipped ornament. The id is the file stem, which is also
 * the key the server resolves to `snippets/<id>.html` — the add-on's slug
 * rule (`^[A-Za-z0-9][A-Za-z0-9_-]*$`) is what the filenames already are.
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
