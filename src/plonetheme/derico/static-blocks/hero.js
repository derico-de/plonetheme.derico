import { useCallback, useEffect, useRef, useState } from "react";
import { Fragment, jsx, jsxs } from "react/jsx-runtime";
import config from "@plone/registry";
function text(value) {
	return typeof value === "string" ? value.trim() : "";
}
/**
* The `@id` of a reference field.
*
* Stored as a one-element list of `{"@id": …}`, but a value that
* never went through the editor may be a bare object or a plain string, and
* neither is worth throwing over.
*/
function reference(value) {
	const first = Array.isArray(value) ? value[0] : value;
	if (typeof first === "string") return first.trim();
	if (first && typeof first === "object") {
		const id = first["@id"];
		if (typeof id === "string") return id.trim();
	}
	return "";
}
/**
* A link renders only when it has BOTH a label and a target.
*
* Symmetric on purpose: no fall back to the target's Title. A fallback would
* make the canvas fetch the target just to agree with the server, and the two
* surfaces would still diverge for the moment between picking and reloading.
*/
function link(label, href) {
	const labelText = text(label);
	const target = reference(href);
	return labelText && target ? {
		label: labelText,
		href: target
	} : null;
}
/**
* The canvas preview URL for a picked image.
*
* One plain scale derived from the `@id`: a freshly picked image has no
* `image_scales` yet, so deriving the URL is the only path that always works.
*/
function previewImage(value) {
	const id = reference(value);
	return id ? `${id.replace(/\/+$/, "")}/@@images/image/large` : "";
}
/** Four entries, always — a shorter or absent list is padded, not rejected. */
function legend(value) {
	const stored = Array.isArray(value) ? value : [];
	return Array.from({ length: 4 }, (_unused, index) => {
		const entry = stored[index] ?? {};
		return {
			title: text(entry.title),
			subtitle: text(entry.subtitle)
		};
	});
}
//#endregion
//#region src/hero/Rings.tsx
/**
* The rings figure: geometry is template, words are content.
*
* The circles, their offsets and the marker positions are the design, not
* data — there is no field for them and no author-facing control. Only the
* four `{title, subtitle}` pairs come from the block; the numerals are
* derived from position, and the `is-now` highlight is the last ring by
* construction.
*
* The legend is HTML beneath the SVG so its captions don't scale with the
* graphic and stay at Clara's 15px label floor.
*
* An empty entry still renders its numeral and rule.
*/
function Rings({ entries }) {
	return /* @__PURE__ */ jsxs("figure", {
		className: "rings-figure",
		children: [/* @__PURE__ */ jsxs("div", {
			className: "rings-stage",
			children: [/* @__PURE__ */ jsxs("svg", {
				className: "rings-disc",
				viewBox: "0 0 680 470",
				role: "img",
				"aria-label": "Wachstumsringe einer Anwendung",
				children: [/* @__PURE__ */ jsxs("g", {
					transform: "translate(105 0)",
					className: "ring-halo",
					children: [
						/* @__PURE__ */ jsx("circle", {
							cx: "150",
							cy: "235",
							r: "40",
							className: "ring-thin"
						}),
						/* @__PURE__ */ jsx("circle", {
							cx: "153",
							cy: "232",
							r: "80"
						}),
						/* @__PURE__ */ jsx("circle", {
							cx: "147",
							cy: "238",
							r: "125",
							className: "ring-thin"
						}),
						/* @__PURE__ */ jsx("circle", {
							cx: "154",
							cy: "231",
							r: "170"
						}),
						/* @__PURE__ */ jsx("circle", {
							cx: "148",
							cy: "237",
							r: "215",
							className: "ring-thin"
						}),
						/* @__PURE__ */ jsx("circle", {
							cx: "152",
							cy: "234",
							r: "250"
						}),
						/* @__PURE__ */ jsx("circle", {
							cx: "150",
							cy: "235",
							r: "290",
							className: "ring-now"
						}),
						/* @__PURE__ */ jsx("circle", {
							cx: "151",
							cy: "234",
							r: "315",
							className: "ring-future"
						})
					]
				}), /* @__PURE__ */ jsxs("g", {
					transform: "translate(105 0)",
					className: "ring-ink",
					children: [
						/* @__PURE__ */ jsx("circle", {
							cx: "150",
							cy: "235",
							r: "40",
							className: "ring-thin"
						}),
						/* @__PURE__ */ jsx("circle", {
							cx: "153",
							cy: "232",
							r: "80"
						}),
						/* @__PURE__ */ jsx("circle", {
							cx: "147",
							cy: "238",
							r: "125",
							className: "ring-thin"
						}),
						/* @__PURE__ */ jsx("circle", {
							cx: "154",
							cy: "231",
							r: "170"
						}),
						/* @__PURE__ */ jsx("circle", {
							cx: "148",
							cy: "237",
							r: "215",
							className: "ring-thin"
						}),
						/* @__PURE__ */ jsx("circle", {
							cx: "152",
							cy: "234",
							r: "250"
						}),
						/* @__PURE__ */ jsx("circle", {
							cx: "150",
							cy: "235",
							r: "290",
							className: "ring-now"
						}),
						/* @__PURE__ */ jsx("circle", {
							cx: "151",
							cy: "234",
							r: "315",
							className: "ring-future"
						})
					]
				})]
			}), /* @__PURE__ */ jsx("ol", {
				className: "ring-markers",
				"aria-hidden": "true",
				children: entries.map((_entry, index) => /* @__PURE__ */ jsx("li", {
					className: index === 3 ? "is-now" : void 0,
					children: index + 1
				}, index))
			})]
		}), /* @__PURE__ */ jsx("dl", {
			className: "ring-legend",
			children: entries.map((entry, index) => /* @__PURE__ */ jsxs("div", {
				className: index === 3 ? "is-now" : void 0,
				children: [
					/* @__PURE__ */ jsx("b", { children: index + 1 }),
					entry.title ? /* @__PURE__ */ jsx("dt", { children: entry.title }) : null,
					entry.subtitle ? /* @__PURE__ */ jsx("dd", { children: entry.subtitle }) : null
				]
			}, index))
		})]
	});
}
//#endregion
//#region src/hero/Hero.tsx
/**
* The Derico Hero, as one component rendered by both `edit` and `view`.
*
* ## `.derico-hero`, not `.block-derico-hero`
*
* Aurora's `block-<@type>` wrapper is the full-bleed box on the public view
* but only the column box in the canvas, so the hero paints on its own root.
*
* ## The hero never sets its own width
*
* The breakout is Blicca's, on the wrapper (public) and the inner container
* (canvas), and `defaultBlockWidth: 'full'` is the whole of the wiring. A
* `width` here would break the equivalence in one surface only.
*
* ## No whitespace-only text nodes
*
* The Plate editable's inherited `white-space: pre-wrap` turns newlines
* between elements into line boxes; JSX drops them, the server template
* must strip its own.
*/
function Hero({ data, media }) {
	const kicker = text(data.kicker);
	const headline = text(data.headline);
	const lede = text(data.lede);
	const cta = link(data.cta_label, data.cta_href);
	const quiet = link(data.link_label, data.link_href);
	const entries = legend(data.legend);
	const hasMedia = Boolean(reference(data.image_wide) || reference(data.image_portrait));
	return /* @__PURE__ */ jsxs("section", {
		className: "derico-hero",
		children: [
			media,
			hasMedia ? /* @__PURE__ */ jsx("div", {
				className: "hero-wash",
				"aria-hidden": "true"
			}) : null,
			/* @__PURE__ */ jsxs("div", {
				className: "home-hero__grid",
				children: [/* @__PURE__ */ jsxs("div", { children: [
					kicker ? /* @__PURE__ */ jsx("p", {
						className: "kicker",
						children: kicker
					}) : null,
					headline ? /* @__PURE__ */ jsx("h1", { children: headline }) : null,
					lede ? /* @__PURE__ */ jsx("p", {
						className: "lede",
						children: lede
					}) : null,
					cta || quiet ? /* @__PURE__ */ jsxs("div", {
						className: "action-row",
						children: [cta ? /* @__PURE__ */ jsx("a", {
							className: "button",
							href: cta.href,
							children: cta.label
						}) : null, quiet ? /* @__PURE__ */ jsx("a", {
							className: "quiet-link",
							href: quiet.href,
							children: quiet.label
						}) : null]
					}) : null
				] }), /* @__PURE__ */ jsx(Rings, { entries })]
			})
		]
	});
}
//#endregion
//#region src/hero/HeroMedia.tsx
/**
* The hero's photograph — one `<picture>`, two crops, art-directed.
*
* Wide and portrait framings are two uploads; the portrait `<source>` comes
* first because `<picture>` takes the first match. `media` is a viewport
* query since `<picture>` has no container-query form.
*
* One plain scale per crop, derived from the `@id`; the public view builds
* the real ladder server-side. One crop → that image everywhere; none →
* `null`.
*
* `aria-hidden`, and no `alt` field anywhere in the schema: the photograph is
* decorative in this design.
*/
function HeroMedia({ data }) {
	const wide = previewImage(data.image_wide);
	const portrait = previewImage(data.image_portrait);
	const fallback = wide || portrait;
	if (!fallback) return null;
	return /* @__PURE__ */ jsxs("picture", {
		className: "hero-media",
		"aria-hidden": "true",
		children: [portrait && wide ? /* @__PURE__ */ jsx("source", {
			media: "(max-width: 55.99rem)",
			srcSet: portrait
		}) : null, /* @__PURE__ */ jsx("img", {
			src: fallback,
			alt: "",
			decoding: "async",
			fetchPriority: "high"
		})]
	});
}
//#endregion
//#region src/hero/defaults.ts
/** The keys the hero owns — everything `HeroSchema` lets an author write. */
var HERO_FIELDS = [
	"kicker",
	"headline",
	"lede",
	"cta_label",
	"cta_href",
	"link_label",
	"link_href",
	"image_wide",
	"image_portrait",
	"legend"
];
var HERO_DEFAULTS = {
	kicker: "Nachhaltige Lösungen, seit über 20 Jahren",
	headline: "Anwendungen, die bleiben.",
	lede: "Wir entwickeln Geschäftsanwendungen auf Basis von Python, modernem JavaScript und Open Source. Wartbarkeit, offene Standards und klare Entscheidungen sichern ihren Wert über viele Jahre.",
	cta_label: "Erstgespräch vereinbaren",
	link_label: "Alle Leistungen",
	legend: [
		{
			title: "schneller Prototyp",
			subtitle: "in Wochen bedienbar"
		},
		{
			title: "erste Anwendung",
			subtitle: "trägt die tägliche Arbeit"
		},
		{
			title: "erfahrener Begleiter",
			subtitle: "wächst mit den Anforderungen"
		},
		{
			title: "mit der Zeit gegangen",
			subtitle: "offen, aktuell, migrierbar"
		}
	]
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
function unseeded(data) {
	return !HERO_FIELDS.some((field) => field in data);
}
/**
* The block data a fresh insert should carry.
*
* A merge, not a replacement: whatever the host already put on the node —
* `@type`, the materialised `blockWidth`, anything a future
* plugin adds — survives untouched.
*/
function seeded(data) {
	return {
		...data,
		...HERO_DEFAULTS
	};
}
//#endregion
//#region src/hero/HeroEdit.tsx
/**
* The `edit` half: the canvas is a live preview, never an editing surface.
*
* Every field is edited in the sidebar; the block is a Plate VOID node. With
* nothing contenteditable, the hero can safely reset the editable's inherited
* `white-space: pre-wrap` to `normal`.
*
* The canvas is also where a fresh insert gets its words. Aurora writes a
* node carrying `@type` and nothing else, and `blocksConfig` has no
* initial-data hook, so this component is the first — and only — place the
* block sees its own node in time to seed it (`defaults.ts`).
*
* The other thing the canvas adds to the public rendering is the nag: a
* half-authored hero saves and previews happily — nothing in the schema is
* required — so the editor is where the author is told what is still missing.
* The hint is `contentEditable={false}` and outside the hero's own root, so
* it can neither be typed into nor styled by the block's palette.
*/
/** What a reader of the finished page would notice was missing. */
function missing(data) {
	const gaps = [];
	if (!text(data.headline)) gaps.push("headline");
	if (!text(data.lede)) gaps.push("lede");
	if (!link(data.cta_label, data.cta_href)) gaps.push("primary call to action");
	if (!reference(data.image_wide)) gaps.push("wide image");
	if (legend(data.legend).every((entry) => !entry.title && !entry.subtitle)) gaps.push("ring legend");
	return gaps;
}
function HeroEdit({ block, data, onChangeBlock }) {
	const seedWritten = useRef(false);
	useEffect(() => {
		if (seedWritten.current || !onChangeBlock || !unseeded(data)) return;
		seedWritten.current = true;
		onChangeBlock(block ?? "", seeded(data));
	}, [
		block,
		data,
		onChangeBlock
	]);
	const gaps = missing(data);
	return /* @__PURE__ */ jsxs(Fragment, { children: [/* @__PURE__ */ jsx(Hero, {
		data,
		media: /* @__PURE__ */ jsx(HeroMedia, { data })
	}), gaps.length ? /* @__PURE__ */ jsxs("p", {
		className: "derico-hero-incomplete",
		contentEditable: false,
		children: [
			"Still to fill in: ",
			gaps.join(", "),
			"."
		]
	}) : null] });
}
//#endregion
//#region src/hero/HeroIcon.tsx
/**
* The slash-menu icon: the growth rings, reduced to what survives at 24px.
*
* A React component, never a string — the slash menu renders `<Icon />` and a
* string breaks it; a missing icon falls back to Aurora's `Square`
* placeholder, which tells the author nothing.
*
* `currentColor` throughout, so the menu's own palette drives it.
*/
function HeroIcon(props) {
	return /* @__PURE__ */ jsxs("svg", {
		viewBox: "0 0 24 24",
		fill: "none",
		stroke: "currentColor",
		strokeWidth: "1.5",
		"aria-hidden": "true",
		focusable: "false",
		...props,
		children: [
			/* @__PURE__ */ jsx("circle", {
				cx: "10",
				cy: "13",
				r: "2.5"
			}),
			/* @__PURE__ */ jsx("circle", {
				cx: "10.5",
				cy: "12.5",
				r: "5.5"
			}),
			/* @__PURE__ */ jsx("circle", {
				cx: "10",
				cy: "13",
				r: "8.5",
				strokeWidth: "2.25"
			}),
			/* @__PURE__ */ jsx("circle", {
				cx: "10.4",
				cy: "12.6",
				r: "11",
				strokeDasharray: "2 3"
			})
		]
	});
}
//#endregion
//#region src/hero/HeroView.tsx
/**
* The `view` half (contract §1.1).
*
* On a Blicca site nothing renders this: the published page is drawn by the
* server view `@@aurora-block-derico-hero`, which builds the real resolution
* ladder. It is implemented anyway, and not as a stub, because the contract's
* single-ecosystem exemption for a brand block covers PUBLICATION only — a
* brand block that skips `view` is not exempt, it is broken, and it renders
* blank the day the site is served through Aurora proper.
*/
function HeroView({ data }) {
	return /* @__PURE__ */ jsx(Hero, {
		data,
		media: /* @__PURE__ */ jsx(HeroMedia, { data })
	});
}
//#endregion
//#region src/hero/schema.ts
/**
* The Derico Hero's sidebar form (contract §1.5).
*
* Deliberately inflexible: the design's text and images and nothing else. No
* width control, no palette variant, no "hide the rings" toggle — a brand
* block implements one design template and offers the author no options.
*
* Two omissions are load-bearing:
*
* - **No `blockWidth`.** The width is template, not content. Aurora resolves a
*   ploneBlock's width as `styleFields.blockWidth ?? defaultBlockWidth`, so
*   declaring the field here would hand the control back and silently undo
*   `defaultBlockWidth: 'full'` in index.tsx (contract §1.4).
* - **Nothing in `required`.** A half-authored hero has to save and preview;
*   the renderers omit what is missing (see data.ts).
*/
var HERO_BLOCK_TYPE = "derico-hero";
/**
* `object_browser` options ride Aurora's own `widgetOptions.pattern_options`
* envelope (contract §1.5), not top-level schema keys. plone.restapi already
* serializes relation fields this way, so a schema written like this keeps
* working if Blicca's widget substitution is ever dropped for Aurora's.
*/
var imagePick = (title) => ({
	title,
	widget: "derico_reference",
	mode: "single",
	widgetOptions: { pattern_options: {
		selectableTypes: ["Image"],
		upload: true
	} }
});
var contentPick = (title) => ({
	title,
	widget: "derico_reference",
	mode: "single"
});
var HeroSchema = {
	title: "Derico Hero",
	/**
	* Three groups, because one flat list of ten fields buried the ring legend
	* — eight nested inputs — under everything else in a narrow sidebar.
	*
	* cmsui renders one accordion per fieldset and expands only the one whose
	* id is literally `default` (`BlockSettingsFormRenderer.tsx`), so the words
	* the author reaches for first stay open and the two heavier groups start
	* folded. The id is load-bearing: rename it and the form opens closed.
	*/
	fieldsets: [
		{
			id: "default",
			title: "Default",
			fields: [
				"kicker",
				"headline",
				"lede",
				"cta_label",
				"link_label"
			]
		},
		{
			id: "targets",
			title: "Targets and images",
			fields: [
				"cta_href",
				"link_href",
				"image_wide",
				"image_portrait"
			]
		},
		{
			id: "legend",
			title: "Ring legend",
			fields: ["legend"]
		}
	],
	required: [],
	properties: {
		kicker: { title: "Kicker" },
		headline: { title: "Headline" },
		lede: {
			title: "Lede",
			widget: "derico_textarea"
		},
		cta_label: { title: "Primary call to action" },
		cta_href: contentPick("Primary target"),
		link_label: { title: "Secondary link" },
		link_href: contentPick("Secondary target"),
		image_wide: imagePick("Wide image"),
		image_portrait: imagePick("Portrait image"),
		legend: {
			title: "Ring legend",
			widget: "derico_ring_legend"
		}
	}
};
//#endregion
//#region src/hero/widgets/ReferenceWidget.tsx
/**
* `derico_reference` — an `object_browser` pick, trimmed to a bare `@id`.
*
* ## Why this widget exists at all
*
* The stored shape is `[{"@id": "../resolveuid/<uid>"}]`. The sidebar writes
* straight onto the Plate node, bypassing the edit component, so a widget is
* the only seam where the trim can happen.
*
* ## Why trim
*
* The content browser returns an enriched brain — `UID`, `title`,
* `review_state`, `image_field`, `image_scales`. Persisting all of it stores a
* snapshot of ANOTHER object's metadata that nothing ever refreshes. The
* server re-derives `image_field` and restapi strips `image_scales` on save,
* so nothing is lost. `selectedItemAttrs` will not do it for us — Blicca's
* widget ignores the list and always fetches the full contract field set.
*
* Options travel on `widgetOptions.pattern_options`, Aurora's own envelope
* (contract §1.5); this widget forwards the whole props bag, so it neither
* knows nor cares which keys the host reads.
*/
/** The stored shape: a one-element list of `{"@id": …}`, or nothing at all. */
function trim(selected) {
	const id = (selected?.[0])?.["@id"];
	return typeof id === "string" && id ? [{ "@id": id }] : void 0;
}
function DericoReferenceWidget(props) {
	const { onChange } = props;
	const [picked, setPicked] = useState(() => reference(props.value ?? props.defaultValue));
	const ObjectBrowser = config.getWidget("object_browser");
	const onSelect = useCallback((selected) => {
		const trimmed = trim(selected);
		setPicked(trimmed ? trimmed[0]["@id"] : "");
		onChange?.(trimmed);
	}, [onChange]);
	const onClear = useCallback(() => {
		setPicked("");
		onChange?.(void 0);
	}, [onChange]);
	return /* @__PURE__ */ jsxs("div", {
		className: "derico-hero-widget derico-hero-widget--reference",
		children: [
			props.label ? /* @__PURE__ */ jsx("label", { children: props.label }) : null,
			picked ? /* @__PURE__ */ jsxs("p", {
				className: "derico-hero-widget__picked",
				children: [/* @__PURE__ */ jsx("span", {
					title: picked,
					children: picked.split("/").filter(Boolean).pop()
				}), /* @__PURE__ */ jsx("button", {
					type: "button",
					onClick: onClear,
					children: "Clear"
				})]
			}) : null,
			ObjectBrowser ? /* @__PURE__ */ jsx(ObjectBrowser, {
				...props,
				label: void 0,
				description: void 0,
				mode: props.mode ?? "single",
				onChange: onSelect
			}) : /* @__PURE__ */ jsx("p", {
				className: "derico-hero-widget__description",
				children: "No content browser is registered in this editor."
			}),
			props.description ? /* @__PURE__ */ jsx("p", {
				className: "derico-hero-widget__description",
				children: props.description
			}) : null
		]
	});
}
//#endregion
//#region src/hero/widgets/RingLegendWidget.tsx
/**
* `derico_ring_legend` — the four `{title, subtitle}` pairs beneath the rings.
*
* Exactly four, always: the numerals are derived from position and the "now"
* highlight is unambiguously the last one, so the count is a template
* invariant both halves may assert rather than defend against. Aurora has no
* object-list widget, hence this one; an array rather than eight flat keys
* keeps a fifth ring a template change, not a data migration.
*
* Writes the WHOLE four-element array on every keystroke. Uncontrolled inputs
* over a ref, for the same reason as the textarea: cmsui hands widgets a
* `defaultValue` and re-renders the form on each change, and a controlled
* input in that loop loses the caret on every character.
*/
function DericoRingLegendWidget(props) {
	const { onChange } = props;
	const entries = useRef(legend(props.value ?? props.defaultValue));
	const update = useCallback((index, key, next) => {
		entries.current = entries.current.map((entry, position) => position === index ? {
			...entry,
			[key]: next
		} : entry);
		onChange?.(entries.current);
	}, [onChange]);
	const fieldId = props.id ?? props.name ?? "legend";
	return /* @__PURE__ */ jsxs("fieldset", {
		className: "derico-hero-widget derico-hero-widget--legend",
		children: [
			props.label ? /* @__PURE__ */ jsx("legend", { children: props.label }) : null,
			Array.from({ length: 4 }, (_unused, index) => /* @__PURE__ */ jsxs("div", {
				className: index === 3 ? "derico-hero-widget__ring is-now" : "derico-hero-widget__ring",
				children: [
					/* @__PURE__ */ jsx("span", {
						"aria-hidden": "true",
						children: index + 1
					}),
					/* @__PURE__ */ jsx("label", {
						htmlFor: `${fieldId}-${index}-title`,
						children: "Title"
					}),
					/* @__PURE__ */ jsx("input", {
						id: `${fieldId}-${index}-title`,
						type: "text",
						defaultValue: entries.current[index].title,
						onChange: (event) => update(index, "title", event.target.value)
					}),
					/* @__PURE__ */ jsx("label", {
						htmlFor: `${fieldId}-${index}-subtitle`,
						children: "Caption"
					}),
					/* @__PURE__ */ jsx("input", {
						id: `${fieldId}-${index}-subtitle`,
						type: "text",
						defaultValue: entries.current[index].subtitle,
						onChange: (event) => update(index, "subtitle", event.target.value)
					})
				]
			}, index)),
			props.description ? /* @__PURE__ */ jsx("p", {
				className: "derico-hero-widget__description",
				children: props.description
			}) : null
		]
	});
}
//#endregion
//#region src/hero/widgets/TextareaWidget.tsx
function DericoTextareaWidget(props) {
	const initial = props.value ?? props.defaultValue ?? "";
	const fieldId = props.id ?? props.name;
	return /* @__PURE__ */ jsxs("div", {
		className: "derico-hero-widget",
		children: [
			props.label ? /* @__PURE__ */ jsx("label", {
				htmlFor: fieldId,
				children: props.label
			}) : null,
			/* @__PURE__ */ jsx("textarea", {
				id: fieldId,
				name: props.name,
				rows: 4,
				defaultValue: typeof initial === "string" ? initial : "",
				placeholder: props.placeholder,
				onChange: (event) => props.onChange?.(event.target.value)
			}),
			props.description ? /* @__PURE__ */ jsx("p", {
				className: "derico-hero-widget__description",
				children: props.description
			}) : null
		]
	});
}
//#endregion
//#region src/hero/index.tsx
function installDericoHero(config) {
	config.registerWidget?.({
		key: "widget",
		definition: {
			derico_textarea: DericoTextareaWidget,
			derico_ring_legend: DericoRingLegendWidget,
			derico_reference: DericoReferenceWidget
		}
	});
	config.blocks.blocksConfig[HERO_BLOCK_TYPE] = {
		id: HERO_BLOCK_TYPE,
		title: "Derico Hero",
		icon: HeroIcon,
		edit: HeroEdit,
		view: HeroView,
		blockSchema: HeroSchema,
		defaultBlockWidth: "full"
	};
	return config;
}
//#endregion
export { HERO_BLOCK_TYPE, installDericoHero as default };

//# sourceMappingURL=hero.js.map