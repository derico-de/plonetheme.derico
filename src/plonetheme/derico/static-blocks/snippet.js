import { useEffect, useRef } from "react";
import { jsx, jsxs } from "react/jsx-runtime";
//#endregion
//#region src/snippet/snippets.ts
/**
* The snippet corpus, imported `?raw` from the Python package's own
* `snippets/` directory — the same files `browser/snippet.py` reads at render
* time. Neither half owns a copy, so the canvas and the published page cannot
* drift: there is exactly one Balkenlage and exactly one Ständerwerk, and
* both surfaces inject it verbatim.
*
* Adding a snippet is: one file in `snippets/`, one import and map entry
* here, one choice in `schema.ts`. `tests/test_snippet_view.py` holds the
* file list and the choice list in lockstep from the Python side.
*/
var SNIPPETS = {
	balkenlage: "<div class=\"balkenlage\" aria-hidden=\"true\">\n  <span class=\"balkenlage__dielen\"></span>\n  <span class=\"balkenlage__lage\"><span class=\"balkenlage__balken\" style=\"--i:0\">\n    <svg viewBox=\"0 0 52 28\" aria-hidden=\"true\" focusable=\"false\">\n      <rect class=\"balken-body\" x=\"0.75\" y=\"0.75\" width=\"50.5\" height=\"26.5\"/>\n      <svg x=\"1.5\" y=\"1.5\" width=\"49\" height=\"25\" viewBox=\"1.5 1.5 49 25\">\n        <g class=\"balken-ringe\"><circle cx=\"16\" cy=\"20\" r=\"1.4\" class=\"balken-mark\"/>\n    <circle cx=\"16\" cy=\"20\" r=\"4\"/>\n    <circle cx=\"16\" cy=\"20\" r=\"10\"/>\n    <circle cx=\"16\" cy=\"20\" r=\"19\"/>\n    <circle cx=\"16\" cy=\"20\" r=\"30\"/></g>\n      </svg>\n    </svg>\n  </span><span class=\"balkenlage__balken\" style=\"--i:1\" data-stoss=\"\">\n    <svg viewBox=\"0 0 52 28\" aria-hidden=\"true\" focusable=\"false\">\n      <rect class=\"balken-body\" x=\"0.75\" y=\"0.75\" width=\"50.5\" height=\"26.5\"/>\n      <svg x=\"1.5\" y=\"1.5\" width=\"49\" height=\"25\" viewBox=\"1.5 1.5 49 25\">\n        <g class=\"balken-ringe\"><circle cx=\"-10\" cy=\"40\" r=\"24\"/>\n    <circle cx=\"-10\" cy=\"40\" r=\"40\"/>\n    <circle cx=\"-10\" cy=\"40\" r=\"58\"/></g>\n      </svg>\n    </svg>\n  </span><span class=\"balkenlage__balken\" style=\"--i:2\">\n    <svg viewBox=\"0 0 52 28\" aria-hidden=\"true\" focusable=\"false\">\n      <rect class=\"balken-body\" x=\"0.75\" y=\"0.75\" width=\"50.5\" height=\"26.5\"/>\n      <svg x=\"1.5\" y=\"1.5\" width=\"49\" height=\"25\" viewBox=\"1.5 1.5 49 25\">\n        <g class=\"balken-ringe\"><circle cx=\"38\" cy=\"8\" r=\"1.4\" class=\"balken-mark\"/>\n    <circle cx=\"38\" cy=\"8\" r=\"4\"/>\n    <circle cx=\"38\" cy=\"8\" r=\"9\"/>\n    <circle cx=\"38\" cy=\"8\" r=\"17\"/>\n    <circle cx=\"38\" cy=\"8\" r=\"28\"/></g>\n      </svg>\n    </svg>\n  </span><span class=\"balkenlage__balken\" style=\"--i:3\">\n    <svg viewBox=\"0 0 52 28\" aria-hidden=\"true\" focusable=\"false\">\n      <rect class=\"balken-body\" x=\"0.75\" y=\"0.75\" width=\"50.5\" height=\"26.5\"/>\n      <svg x=\"1.5\" y=\"1.5\" width=\"49\" height=\"25\" viewBox=\"1.5 1.5 49 25\">\n        <g class=\"balken-ringe\"><circle cx=\"-10\" cy=\"40\" r=\"24\"/>\n    <circle cx=\"-10\" cy=\"40\" r=\"40\"/>\n    <circle cx=\"-10\" cy=\"40\" r=\"58\"/></g>\n      </svg>\n    </svg>\n  </span><span class=\"balkenlage__balken\" style=\"--i:4\">\n    <svg viewBox=\"0 0 52 28\" aria-hidden=\"true\" focusable=\"false\">\n      <rect class=\"balken-body\" x=\"0.75\" y=\"0.75\" width=\"50.5\" height=\"26.5\"/>\n      <svg x=\"1.5\" y=\"1.5\" width=\"49\" height=\"25\" viewBox=\"1.5 1.5 49 25\">\n        <g class=\"balken-ringe\"><circle cx=\"74\" cy=\"14\" r=\"32\"/>\n    <circle cx=\"74\" cy=\"14\" r=\"45\"/>\n    <circle cx=\"74\" cy=\"14\" r=\"60\"/></g>\n      </svg>\n    </svg>\n  </span><span class=\"balkenlage__balken\" style=\"--i:5\" data-stoss=\"\">\n    <svg viewBox=\"0 0 52 28\" aria-hidden=\"true\" focusable=\"false\">\n      <rect class=\"balken-body\" x=\"0.75\" y=\"0.75\" width=\"50.5\" height=\"26.5\"/>\n      <svg x=\"1.5\" y=\"1.5\" width=\"49\" height=\"25\" viewBox=\"1.5 1.5 49 25\">\n        <g class=\"balken-ringe\"><circle cx=\"16\" cy=\"20\" r=\"1.4\" class=\"balken-mark\"/>\n    <circle cx=\"16\" cy=\"20\" r=\"4\"/>\n    <circle cx=\"16\" cy=\"20\" r=\"10\"/>\n    <circle cx=\"16\" cy=\"20\" r=\"19\"/>\n    <circle cx=\"16\" cy=\"20\" r=\"30\"/></g>\n      </svg>\n    </svg>\n  </span><span class=\"balkenlage__balken\" style=\"--i:6\">\n    <svg viewBox=\"0 0 52 28\" aria-hidden=\"true\" focusable=\"false\">\n      <rect class=\"balken-body\" x=\"0.75\" y=\"0.75\" width=\"50.5\" height=\"26.5\"/>\n      <svg x=\"1.5\" y=\"1.5\" width=\"49\" height=\"25\" viewBox=\"1.5 1.5 49 25\">\n        <g class=\"balken-ringe\"><circle cx=\"38\" cy=\"8\" r=\"1.4\" class=\"balken-mark\"/>\n    <circle cx=\"38\" cy=\"8\" r=\"4\"/>\n    <circle cx=\"38\" cy=\"8\" r=\"9\"/>\n    <circle cx=\"38\" cy=\"8\" r=\"17\"/>\n    <circle cx=\"38\" cy=\"8\" r=\"28\"/></g>\n      </svg>\n    </svg>\n  </span><span class=\"balkenlage__balken\" style=\"--i:7\">\n    <svg viewBox=\"0 0 52 28\" aria-hidden=\"true\" focusable=\"false\">\n      <rect class=\"balken-body\" x=\"0.75\" y=\"0.75\" width=\"50.5\" height=\"26.5\"/>\n      <svg x=\"1.5\" y=\"1.5\" width=\"49\" height=\"25\" viewBox=\"1.5 1.5 49 25\">\n        <g class=\"balken-ringe\"><circle cx=\"74\" cy=\"14\" r=\"32\"/>\n    <circle cx=\"74\" cy=\"14\" r=\"45\"/>\n    <circle cx=\"74\" cy=\"14\" r=\"60\"/></g>\n      </svg>\n    </svg>\n  </span></span>\n</div>\n",
	"service-frame": "<div class=\"derico-staenderwerk\" aria-hidden=\"true\">\n  <span class=\"service-frame\" aria-hidden=\"true\">\n    <span class=\"service-frame__schwelle\"></span>\n    <svg class=\"service-frame__gebinde service-frame__gebinde--start\" viewBox=\"0 0 210 190\" aria-hidden=\"true\" focusable=\"false\">\n    <g class=\"frame-beam\">\n      <path d=\"M20 16h40v174H20Z\"/>\n      <path d=\"M60 62 188 190h-45L60 107Z\"/>\n    </g>\n    <g class=\"frame-grain\">\n      <path d=\"M20 24h40\"/>\n      <path d=\"M32 30c3 44-2 90 1 152\"/>\n      <path d=\"M82 104 160 182\"/>\n    </g>\n    <g class=\"frame-ast\">\n      <ellipse cx=\"48\" cy=\"120\" rx=\"5\" ry=\"6.8\"/>\n      <ellipse cx=\"48\" cy=\"120\" rx=\"1.9\" ry=\"2.6\"/>\n    </g>\n    <g class=\"frame-zapfen\">\n      <circle cx=\"40\" cy=\"85\" r=\"7\"/>\n      <circle cx=\"40\" cy=\"168\" r=\"7\"/>\n    </g>\n  </svg>\n    <svg class=\"service-frame__gebinde service-frame__gebinde--end\" viewBox=\"0 0 210 190\" aria-hidden=\"true\" focusable=\"false\">\n    <g class=\"frame-beam\">\n      <path d=\"M20 16h40v174H20Z\"/>\n      <path d=\"M60 62 188 190h-45L60 107Z\"/>\n    </g>\n    <g class=\"frame-grain\">\n      <path d=\"M20 24h40\"/>\n      <path d=\"M32 30c3 44-2 90 1 152\"/>\n      <path d=\"M82 104 160 182\"/>\n    </g>\n    <g class=\"frame-ast\">\n      <ellipse cx=\"48\" cy=\"120\" rx=\"5\" ry=\"6.8\"/>\n      <ellipse cx=\"48\" cy=\"120\" rx=\"1.9\" ry=\"2.6\"/>\n    </g>\n    <g class=\"frame-zapfen\">\n      <circle cx=\"40\" cy=\"85\" r=\"7\"/>\n      <circle cx=\"40\" cy=\"168\" r=\"7\"/>\n    </g>\n  </svg>\n  </span>\n</div>\n"
};
var DEFAULT_SNIPPET = "balkenlage";
/**
* The markup for a node's stored key. The value is untrusted in exactly the
* way the server view's is — the block is authorable through the API — and is
* only ever a lookup key: unknown or absent falls back to the Balkenlage,
* mirroring `DericoSnippetView.markup`.
*/
function markup(data) {
	return SNIPPETS[data?.snippet ?? ""] ?? SNIPPETS["balkenlage"];
}
//#endregion
//#region src/snippet/Snippet.tsx
/**
* The one rendering both halves share: the stored key's fragment, injected
* verbatim. `dangerouslySetInnerHTML` is safe by construction here — the
* markup never comes from the node, only the LOOKUP KEY does, and the corpus
* is the package's own `snippets/*.html` (see snippets.ts).
*/
function Snippet({ data }) {
	return /* @__PURE__ */ jsx("div", {
		className: "derico-snippet",
		dangerouslySetInnerHTML: { __html: markup(data) }
	});
}
//#endregion
//#region src/snippet/SnippetEdit.tsx
/**
* The `edit` half: the canvas preview, plus the one write this block ever
* makes to its own node.
*
* Aurora's slash menu creates a node carrying `@type` and nothing else, and
* `blocksConfig` has no initial-data hook, so — exactly as `HeroEdit` does —
* the freshly inserted block seeds itself, here with the schema's own
* default. Without the seed the renderers would still fall back to the
* Balkenlage (snippets.ts / snippet.py), but the sidebar select would sit on
* an unstored value: what the author sees claimed and what the node says
* would disagree until the first manual change.
*
* No nag and no in-canvas editing: the block has no text, and a snippet with
* its default stored is already finished.
*/
function SnippetEdit({ block, data, onChangeBlock }) {
	const seedWritten = useRef(false);
	const unseeded = data?.snippet === void 0;
	useEffect(() => {
		if (!unseeded || seedWritten.current || !block || !onChangeBlock) return;
		seedWritten.current = true;
		onChangeBlock(block, {
			...data,
			snippet: DEFAULT_SNIPPET
		});
	}, [
		unseeded,
		block,
		data,
		onChangeBlock
	]);
	return /* @__PURE__ */ jsx(Snippet, { data });
}
//#endregion
//#region src/snippet/SnippetIcon.tsx
/**
* The slash-menu icon: the Balkenlage in section, reduced to what survives at
* 24px — the Dielen band and three Balkenköpfe beneath it.
*
* A React component, never a string, `currentColor` throughout — same rules
* as `HeroIcon`.
*/
function SnippetIcon(props) {
	return /* @__PURE__ */ jsxs("svg", {
		viewBox: "0 0 24 24",
		fill: "none",
		stroke: "currentColor",
		strokeWidth: "1.5",
		"aria-hidden": "true",
		focusable: "false",
		...props,
		children: [
			/* @__PURE__ */ jsx("path", { d: "M2 8h20" }),
			/* @__PURE__ */ jsx("path", { d: "M2 11h20" }),
			/* @__PURE__ */ jsx("rect", {
				x: "3.5",
				y: "11",
				width: "4.5",
				height: "3.5"
			}),
			/* @__PURE__ */ jsx("rect", {
				x: "9.75",
				y: "11",
				width: "4.5",
				height: "3.5"
			}),
			/* @__PURE__ */ jsx("rect", {
				x: "16",
				y: "11",
				width: "4.5",
				height: "3.5"
			})
		]
	});
}
//#endregion
//#region src/snippet/SnippetView.tsx
/**
* The `view` half (contract §1.1).
*
* On a Blicca site nothing renders this: the published page is drawn by the
* server view `@@aurora-block-derico-snippet`, which injects the same file
* this bundle imported `?raw`. Implemented anyway, and trivially real rather
* than a stub, for the same reason the hero's is: the contract's
* single-ecosystem exemption covers publication only.
*/
function SnippetView({ data }) {
	return /* @__PURE__ */ jsx(Snippet, { data });
}
//#endregion
//#region src/snippet/schema.ts
/**
* The Derico Snippet's sidebar form: one choice, nothing else.
*
* A brand block gains a variant only when the design itself demands one, and
* this block IS that case: the design ships several static ornaments that
* differ in nothing but their markup, so the variant field is the block's
* whole reason to be generic. `choices` is what makes the wrapper render a
* select (its registered `choices` widget slot) — no custom widget needed.
*
* No `blockWidth`, same interlock as the hero: the width is template, not
* content. `defaultBlockWidth: 'layout'` in index.tsx fixes it at the shell
* width the mockup places both ornaments at, and a `blockWidth` property here
* would silently hand the control back (contract §1.4).
*/
var SNIPPET_BLOCK_TYPE = "derico-snippet";
var SnippetSchema = {
	title: "Derico Snippet",
	fieldsets: [{
		id: "default",
		title: "Default",
		fields: ["snippet"]
	}],
	required: [],
	properties: { snippet: {
		title: "Snippet",
		choices: [["balkenlage", "Balkenlage (Trenner)"], ["service-frame", "Ständerwerk (Rahmen)"]],
		default: "balkenlage"
	} }
};
//#endregion
//#region src/snippet/index.tsx
/**
* The Derico Snippet's bundle entry point.
*
* Same registration contract as the hero's (contract §1.3): the default
* export is the install function, called once per registration record, and it
* MUST return the config object. Its own bundle and its own record rather
* than a line in the hero's install, because `loadBlockAddons` calls
* `install(config)` per RECORD with no dedupe — a shared bundle would kill
* the per-block `enabled` kill switch (hero ticket 04 §1).
*
* Two things the hero's entry does that this one deliberately does not:
*
* - **No CSS import.** The snippets are styled by the theme's own
*   `static/snippets.css` bundle, hand-scope-wrapped; this bundle ships only
*   markup and registration, so the build's shared `blocks.css` stays the
*   hero's alone and the record declares no `css`.
* - **No widget registrations.** One `choices` field is vocabulary the
*   wrapper already provides.
*/
function installDericoSnippet(config) {
	config.blocks.blocksConfig[SNIPPET_BLOCK_TYPE] = {
		id: SNIPPET_BLOCK_TYPE,
		title: "Derico Snippet",
		icon: SnippetIcon,
		edit: SnippetEdit,
		view: SnippetView,
		blockSchema: SnippetSchema,
		defaultBlockWidth: "layout"
	};
	return config;
}
//#endregion
export { SNIPPET_BLOCK_TYPE, installDericoSnippet as default };

//# sourceMappingURL=snippet.js.map