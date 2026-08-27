"""Installing the Derico Hero: the record, the imaging, the gate, the upgrade.

The renderer is only half the server half. The other half is packaging, and
almost all of it fails SILENTLY when it is wrong: a `block_api` a notch too
high, a bundle path that does not resolve, a `types` list that does not match
the `@type` the bundle registers — every one of those is a fail-soft skip
(contract §2.4/§5.5), and the symptom is a block that is simply not in the
slash menu. Nothing raises, nothing logs at render time, and the author
reports "the hero is gone".

So the assertions here are mostly Blicca's own verdicts rather than the
record's raw values: `evaluate()` is what @@aurora-edit runs, and a record
that satisfies it is a record that works.
"""

import pytest
from plone import api
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.base.interfaces import IImagingSchema
from plone.blicca.auroraeditor import blockaddons
from plone.blicca.auroraeditor.interfaces import IPloneBliccaAuroraeditorLayer
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.interface import alsoProvides

from plonetheme.derico.interfaces import IPlonethemeDericoLayer
from plonetheme.derico.setuphandlers import ensure_hero_variants
from plonetheme.derico.setuphandlers import HERO_VARIANTS


#: The collection prefix is separated from the record name by a SLASH;
#: only the field below it is dotted.
RECORD = "plone.blicca.auroraeditor.blockaddons/plonetheme.derico.hero"
BLOCK_TYPE = "derico-hero"
PERMISSION = "plonetheme.derico: Insert Brand Block"
NEW_SCALE = "enormous 2600:65536"
STATIC_BASE = "++plone++plonetheme.derico.blocks"


def record(name, default=None):
    return api.portal.get_registry_record(f"{RECORD}.{name}", default=default)


class InstallTestCase:
    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        self.request = integration["request"]
        alsoProvides(self.request, IPlonethemeDericoLayer)
        alsoProvides(self.request, IPloneBliccaAuroraeditorLayer)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        login(self.portal, TEST_USER_NAME)

    def status(self):
        """The hero's record, as Blicca's own discovery sees it."""
        found = [
            status
            for status in blockaddons.evaluate(self.portal)
            if status.name == "plonetheme.derico.hero"
        ]
        assert found, "the hero's record is not discovered as a block add-on"
        return found[0]


class TestTheHost(InstallTestCase):
    """Ticket 04 §12: a Python dependency does not install a profile."""

    def test_the_editor_is_installed_with_the_theme(self):
        installer = api.addon.get_installer(self.portal)
        assert installer.is_product_installed("plone.blicca.auroraeditor")

    def test_the_theme_declares_a_python_floor_on_it(self):
        """`block_api` versions the JS facades alone (contract §2.2/§5.2).

        `browser/hero.py` imports `image_source` and `path_of` from
        `plone.blicca.auroraeditor.rendering`, and no record field says
        anything about those — the distribution version is the only signal,
        so it has to be a real floor and not a bare requirement.
        """
        from importlib.metadata import requires

        from packaging.requirements import Requirement
        from packaging.utils import canonicalize_name

        # Dist metadata normalises the name, so match on the normal form
        # rather than on the spelling pyproject.toml uses.
        floors = [
            requirement
            for requirement in (Requirement(line) for line in requires("plonetheme.derico") or [])
            if canonicalize_name(requirement.name) == "plone-blicca-auroraeditor"
        ]
        assert floors, "the hero's host is not a declared dependency at all"
        assert str(floors[0].specifier), (
            "plone.blicca.auroraeditor is depended on without a version "
            "floor, so nothing stops an install resolving a release that "
            "predates image_source / path_of"
        )

    def test_the_promised_rendering_api_is_importable(self):
        """The floor is a claim about these three names."""
        from plone.blicca.auroraeditor.rendering import BaseBlockView
        from plone.blicca.auroraeditor.rendering import image_source
        from plone.blicca.auroraeditor.rendering import path_of

        assert BaseBlockView and image_source and path_of


class TestTheBlockRecord(InstallTestCase):
    def test_the_record_is_discovered(self):
        assert self.status().name == "plonetheme.derico.hero"

    def test_the_record_is_loadable(self):
        """Every filter gate passed: enabled, resolvable, compatible."""
        status = self.status()
        assert status.loadable, f"the hero would be skipped: {status.skip_reason}"

    def test_the_bundle_url_resolves(self):
        """A record whose bundle does not resolve is skipped with a warning."""
        assert self.status().bundle_url

    def test_the_stylesheet_url_resolves(self):
        assert self.status().css_url

    def test_the_assets_are_served_from_the_block_directory(self):
        """`++plone++`, not `++resource++` (ticket 04 §3).

        The contract's cache-buster names `++plone++`, and one directory
        registered under both directives would give every file two public
        URLs — two URLs for one JS module is the duplicate-React failure the
        contract exists to prevent.
        """
        assert record("bundle") == f"{STATIC_BASE}/hero.js"
        assert record("css") == f"{STATIC_BASE}/blocks.css"

    def test_the_stylesheet_is_the_shared_one(self):
        """Lib mode emits ONE sheet per build, not per entry (ticket 04 §5).

        Every future brand block's record names this same file, so a record
        pointing at a per-block sheet is a build that has silently changed
        shape.
        """
        assert record("css").endswith("/blocks.css")

    def test_the_record_declares_the_block_type(self):
        """`types` is diagnostics AND the insert gate, never dispatch."""
        assert tuple(record("types")) == (BLOCK_TYPE,)

    def test_the_record_declares_the_block_api_floor(self):
        """The FLOOR the block needs, not the host's current version.

        Declaring the host's would let a later host bump strand the block,
        and a mismatch is a fail-soft skip. `test_block_addon_lockstep.py`
        guards the other end: that the floor never exceeds what the host has.
        """
        assert record("block_api") == "1.0"

    def test_the_record_is_enabled(self):
        assert record("enabled") is True

    def test_there_is_no_server_renderer_gap(self):
        """Contract §5.5, run for real.

        Blicca reports every registered `@type` whose `aurora-block-<@type>`
        lookup falls through to the default view. The hero appearing here
        would mean the editor offers a block the published page renders as an
        empty `block-unrendered` div.
        """
        gaps = blockaddons.lockstep_gaps(
            self.portal, self.request, blockaddons.evaluate(self.portal)
        )
        assert gaps == [], f"registered blocks with no server renderer: {gaps}"


class TestTheInsertGate(InstallTestCase):
    """Ticket 03's gate, from the theme's side: define it, grant it, name it.

    Guidance, not security — the block stays authorable through the API. What
    is being checked is that the right ROLES hold it, because the failure this
    guards against is silent in the opposite direction: a permission nobody
    holds hides the block from the site administrator the destination names.
    """

    def test_the_record_names_the_permission(self):
        assert record("permission") == PERMISSION

    def test_it_is_a_title_and_not_a_zcml_id(self):
        """`checkPermission` takes titles. An id resolves to Manager-only."""
        assert " " in record("permission")
        assert not record("permission").startswith("plonetheme.derico.")

    def test_a_manager_may_insert_the_hero(self):
        assert blockaddons.may_insert(self.portal, self.status())

    def test_a_site_administrator_may_insert_the_hero(self):
        """The role the destination actually names.

        `cmf.ManagePortal` — the obvious candidate — is held by Manager alone
        in stock Plone and would have locked this role out.
        """
        setRoles(self.portal, TEST_USER_ID, ["Site Administrator"])
        login(self.portal, TEST_USER_NAME)
        assert blockaddons.may_insert(self.portal, self.status())

    def test_an_ordinary_editor_may_not(self):
        setRoles(self.portal, TEST_USER_ID, ["Editor", "Contributor"])
        login(self.portal, TEST_USER_NAME)
        assert not blockaddons.may_insert(self.portal, self.status())

    def test_the_gate_reaches_the_client_as_a_restricted_type(self):
        """The verdict ships as `restrictedBlockTypes`, a list of @types."""
        setRoles(self.portal, TEST_USER_ID, ["Editor"])
        login(self.portal, TEST_USER_NAME)
        assert BLOCK_TYPE in blockaddons.restricted_block_types(self.portal)

    def test_the_grant_acquires_down_the_tree(self):
        """@@aurora-edit checks the object being EDITED, not the root."""
        folder = api.content.create(
            container=self.portal, type="Folder", id="section", title="Section"
        )
        setRoles(self.portal, TEST_USER_ID, ["Site Administrator"])
        login(self.portal, TEST_USER_NAME)
        assert blockaddons.may_insert(folder, self.status())


class TestImaging(InstallTestCase):
    """Ticket 05: a scale rung through GS, two variants through a handler."""

    def _variants(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IImagingSchema, prefix="plone", check=False)
        return dict(settings.picture_variants or {})

    def test_the_new_scale_rung_is_registered(self):
        assert NEW_SCALE in api.portal.get_registry_record("plone.allowed_sizes")

    def test_the_stock_ladder_survived_the_merge(self):
        """`purge="false"` is what makes registry.xml append rather than replace.

        Stock templates and other add-ons hardcode these names; replacing the
        list would break things well outside this theme.
        """
        names = {
            line.split(" ")[0] for line in api.portal.get_registry_record("plone.allowed_sizes")
        }
        assert {"large", "preview", "mini", "thumb", "icon"} <= names

    @pytest.mark.parametrize("name", sorted(HERO_VARIANTS))
    def test_the_hero_variants_are_installed(self, name):
        """A JSONField: GenericSetup has no syntax for one, hence the handler."""
        assert name in self._variants()

    def test_the_wide_variant_carries_the_top_rung(self):
        sourceset = self._variants()["hero-wide"]["sourceset"][0]
        assert sourceset["scale"] == "huge"
        assert "enormous" in sourceset["additionalScales"]

    def test_the_portrait_variant_carries_the_design_breakpoint(self):
        """`<picture>` has no container-query form, so this one is a viewport
        query while the layout switch next door is not — deliberately, and it
        must stay identical to the query `HeroMedia.tsx` writes."""
        sourceset = self._variants()["hero-portrait"]["sourceset"][0]
        assert sourceset["media"] == "(max-width: 55.99rem)"

    @pytest.mark.parametrize("name", sorted(HERO_VARIANTS))
    def test_both_variants_state_their_scales_and_sizes(self, name):
        """Both default to something wrong for a full-bleed block.

        Omitted, `additionalScales` becomes every other allowed scale and
        `sizes` becomes a three-branch query built for in-flow images.
        """
        sourceset = self._variants()[name]["sourceset"][0]
        assert sourceset["additionalScales"]
        assert sourceset["sizes"] == "100vw"

    @pytest.mark.parametrize("name", sorted(HERO_VARIANTS))
    def test_neither_variant_is_offered_in_the_richtext_picker(self, name):
        """They are meaningless for an image placed by hand in a page."""
        assert self._variants()[name]["hideInEditor"] is True

    def test_the_handler_never_overwrites_an_existing_variant(self):
        """Add-only, on Blicca's `ensure_fullwidth_variant` pattern.

        Re-running the profile on a live site must not clobber a variant an
        administrator has since tuned.
        """
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IImagingSchema, prefix="plone", check=False)
        variants = dict(settings.picture_variants or {})
        variants["hero-wide"] = {"title": "Edited by hand", "sourceset": []}
        settings.picture_variants = variants

        ensure_hero_variants()

        assert self._variants()["hero-wide"]["title"] == "Edited by hand"

    def test_the_handler_touches_nothing_it_did_not_create(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IImagingSchema, prefix="plone", check=False)
        variants = dict(settings.picture_variants or {})
        variants["someone-elses"] = {"title": "Theirs", "sourceset": []}
        settings.picture_variants = variants

        ensure_hero_variants()

        assert self._variants()["someone-elses"] == {"title": "Theirs", "sourceset": []}


class TestTheUpgradeStep(InstallTestCase):
    """Profile version 1001: the sites that already have derico at 1000.

    Everything this step does is invisible on a fresh install, which is
    exactly why it is easy to ship without. A site upgraded without it has
    the block bundle on disk, no record pointing at it, no permission, and no
    picture variants.
    """

    def test_the_hero_upgrade_is_no_longer_pending(self):
        """The profile has moved past 1001 (it is at 1002 since the snippet
        block), so what is worth holding is that the 1000→1001 step is not
        still waiting to run — not the literal current version, which the
        newest upgrade's own tests pin."""
        setup_tool = self.portal.portal_setup
        version = setup_tool.getLastVersionForProfile("plonetheme.derico:default")
        assert int(version[0]) >= 1001

    def test_an_upgrade_step_from_1000_is_registered(self):
        setup_tool = self.portal.portal_setup
        steps = setup_tool.listUpgrades("plonetheme.derico:default", show_old=True)
        assert steps, "no upgrade step is registered at all"
        titles = str(steps)
        assert "1001" in titles

    def test_the_handler_is_idempotent(self):
        """It runs import steps and an add-only handler; running it on an
        already-current site must change nothing and raise nothing."""
        from plonetheme.derico.upgrades.v1001 import upgrade

        upgrade(self.portal.portal_setup)

        assert self.status().loadable
        assert NEW_SCALE in api.portal.get_registry_record("plone.allowed_sizes")
        assert "hero-wide" in self._variants_after()

    def _variants_after(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IImagingSchema, prefix="plone", check=False)
        return dict(settings.picture_variants or {})


class TestUninstall:
    """Uninstall is deliberately ASYMMETRIC, and the asymmetry is the point."""

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        login(self.portal, TEST_USER_NAME)
        api.addon.get_installer(self.portal).uninstall_product("plonetheme.derico")

    def test_the_block_record_is_removed(self):
        """An orphaned record would keep offering a block nothing can render."""
        assert record("bundle", default=None) is None
        assert record("types", default=None) is None

    def test_the_scale_rung_is_left_in_place(self):
        """Removing a scale that content elsewhere now references is worse
        than leaving a harmless extra rung in the ladder (ticket 05 §5)."""
        assert NEW_SCALE in api.portal.get_registry_record("plone.allowed_sizes")

    def test_the_picture_variants_are_left_in_place(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IImagingSchema, prefix="plone", check=False)
        assert "hero-wide" in (settings.picture_variants or {})
