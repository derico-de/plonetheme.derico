import { useLayoutEffect, useRef } from "react";
import { jsx, jsxs } from "react/jsx-runtime";
import config from "@plone/registry";
import { atom } from "jotai";
import { useFieldFocusedAtom } from "@plone/helpers";
//#region src/pageheader/InlineField.tsx
/**
* The inline control the canvas draws for one of the header's three texts:
* a bare `<textarea>` sitting exactly where the published page puts the
* words, dressed by the sheet to inherit the element it stands in — so the
* author types INTO the heading and sees the heading.
*
* A textarea for all three, on purpose: the title must wrap like the h1 it
* will become, and an `<input>` cannot. A `line` folds any newline to a
* space and swallows Enter.
*
* A ploneBlock is a Plate void with `contentEditable={false}`, so a native
* control inside it receives focus and text normally — but every key event
* still bubbles to the editor's plugin handlers, where Enter inserts a
* paragraph after the block and Backspace on a selected block removes it.
* The control therefore stops its keyboard and clipboard events at itself
* (contract §1.7). Mouse events are left alone: a click must still select
* the block, so its sidebar opens.
*/
var stop = (event) => event.stopPropagation();
function InlineField({ value, onChange, label, line = false }) {
	const ref = useRef(null);
	useLayoutEffect(() => {
		const element = ref.current;
		if (!element) return;
		element.style.height = "auto";
		element.style.height = `${element.scrollHeight}px`;
	}, [value]);
	return /* @__PURE__ */ jsx("textarea", {
		ref,
		className: "page-header__input",
		rows: 1,
		value,
		placeholder: label,
		"aria-label": label,
		onChange: (event) => {
			const next = event.target.value;
			onChange(line ? next.replace(/[\r\n]+/g, " ") : next);
		},
		onKeyDown: (event) => {
			event.stopPropagation();
			if (line && event.key === "Enter") event.preventDefault();
		},
		onKeyUp: stop,
		onBeforeInput: stop,
		onPaste: stop,
		onCopy: stop,
		onCut: stop,
		onDrop: stop
	});
}
//#endregion
//#region src/pageheader/PageHeader.tsx
function PageHeader({ kicker, title, description }) {
	return /* @__PURE__ */ jsx("section", {
		className: "derico-page-header",
		children: /* @__PURE__ */ jsxs("div", {
			className: "page-header__grid",
			children: [/* @__PURE__ */ jsxs("div", { children: [kicker ? /* @__PURE__ */ jsx("p", {
				className: "page-context",
				children: kicker
			}) : null, title ? /* @__PURE__ */ jsx("h1", {
				className: "documentFirstHeading",
				children: title
			}) : null] }), description ? /* @__PURE__ */ jsx("p", {
				className: "documentDescription lede",
				children: description
			}) : null]
		})
	});
}
//#endregion
//#region src/pageheader/content-fields.ts
/**
* The page's title and description, bound through the host's form atom.
*
* The host keeps the content item being edited in a jotai atom registered
* as the `formAtom` utility; Aurora's title node reads and writes the title
* through it with `useFieldFocusedAtom`, and Blicca's save carries every
* field of that atom the canvas changed (block add-on contract §1.7). This
* block binds `title` and `description` the same way: what the author types
* lands in the atom at once, and Save persists it with the blocks — so a
* page with this block needs neither the tree's title node nor its
* description node, and the field stays what it was when the block goes.
*
* Resolved at render time through the registry, with an inert fallback where
* no host registered one (a test, a bare registry). `jotai` and
* `@plone/helpers` are promised facades (contract §2.1): the bundle imports
* them from the page's import map and never carries a copy.
*/
var fallbackFormAtom = atom({});
/** The host's form atom, or an inert one. */
function formAtom() {
	const registry = config;
	try {
		const method = registry.getUtility?.({
			name: "formAtom",
			type: "atom"
		})?.method;
		return (typeof method === "function" ? method() : null) ?? fallbackFormAtom;
	} catch {
		return fallbackFormAtom;
	}
}
/**
* `[value, setValue]` for one of the page's text fields. `''` while the atom
* does not hold the field as a string — a bare registry, a field cleared to
* `null` by restapi.
*/
function useContentField(field) {
	const [value, setValue] = useFieldFocusedAtom(formAtom(), field);
	return [typeof value === "string" ? value : "", setValue];
}
//#endregion
//#region src/pageheader/data.ts
/** The trimmed text of a value, or `''` for anything that is not text. */
function text(value) {
	return typeof value === "string" ? value.trim() : "";
}
/** The value a control edits: untrimmed, or the author's trailing space is eaten. */
function raw(value) {
	return typeof value === "string" ? value : "";
}
//#endregion
//#region src/pageheader/PageHeaderEdit.tsx
/**
* The `edit` half: the canvas IS the editing surface.
*
* Three inline controls, one per word of the header, each standing where
* the published page puts that word (`InlineField`). The kicker is the
* block's own data and goes through `onChangeBlock`; the title and the
* description are the page's fields and go through the host's form atom
* (`content-fields.ts`, contract §1.7) — the same pair Aurora's title node
* writes, so the two never disagree.
*
* Every slot is always rendered here, empty or not: a slot the author
* cannot see cannot be typed into. The public view omits what is empty.
*/
function PageHeaderEdit({ block, data, onChangeBlock }) {
	const [title, setTitle] = useContentField("title");
	const [description, setDescription] = useContentField("description");
	const setKicker = (kicker) => onChangeBlock?.(block ?? "", {
		...data,
		kicker
	});
	return /* @__PURE__ */ jsx(PageHeader, {
		kicker: /* @__PURE__ */ jsx(InlineField, {
			value: raw(data.kicker),
			onChange: setKicker,
			label: "Kicker"
		}),
		title: /* @__PURE__ */ jsx(InlineField, {
			value: title,
			onChange: setTitle,
			label: "Title",
			line: true
		}),
		description: /* @__PURE__ */ jsx(InlineField, {
			value: description,
			onChange: setDescription,
			label: "Description"
		})
	});
}
//#endregion
//#region src/pageheader/PageHeaderIcon.tsx
/**
* The slash-menu icon: a kicker line, a heading bar, a lede — the header
* reduced to what survives at 24px.
*
* A React component, never a string — the slash menu renders `<Icon />` and a
* string breaks it. `currentColor` throughout, so the menu's palette drives it.
*/
function PageHeaderIcon(props) {
	return /* @__PURE__ */ jsxs("svg", {
		viewBox: "0 0 24 24",
		fill: "none",
		stroke: "currentColor",
		strokeWidth: "1.5",
		strokeLinecap: "round",
		"aria-hidden": "true",
		focusable: "false",
		...props,
		children: [
			/* @__PURE__ */ jsx("path", { d: "M4 5h6" }),
			/* @__PURE__ */ jsx("path", {
				d: "M4 11h11",
				strokeWidth: "3"
			}),
			/* @__PURE__ */ jsx("path", { d: "M4 17h16" }),
			/* @__PURE__ */ jsx("path", { d: "M4 20h12" })
		]
	});
}
//#endregion
//#region src/pageheader/PageHeaderView.tsx
/**
* The `view` half (contract §1.1).
*
* On a Blicca site nothing renders this: the published page is drawn by the
* server view `@@aurora-block-derico-page-header` from the content's own
* Title and Description. It is implemented anyway — a brand block that skips
* `view` renders blank the day the site is served through Aurora proper —
* and it reads the same form atom the canvas writes, which is the content.
*/
function PageHeaderView({ data }) {
	const [title] = useContentField("title");
	const [description] = useContentField("description");
	return /* @__PURE__ */ jsx(PageHeader, {
		kicker: text(data.kicker),
		title: text(title),
		description: text(description)
	});
}
//#endregion
//#region src/pageheader/schema.ts
/**
* The Derico Page Header's sidebar form (contract §1.5).
*
* One field. The title and the description are not here because they are
* not the block's: they are the page's fields, edited on the canvas through
* the host's form atom (`content-fields.ts`) — and a second copy in the
* sidebar would be a second control for the same value. The kicker is here
* as well as on the canvas because the sidebar is where an author looks for
* "what does this block store".
*
* No `blockWidth`: the width is template, not content. Aurora resolves a
* ploneBlock's width as `styleFields.blockWidth ?? defaultBlockWidth`, so
* declaring the field here would hand the control back and silently undo
* `defaultBlockWidth: 'layout'` in index.tsx (contract §1.4).
*/
var PAGE_HEADER_BLOCK_TYPE = "derico-page-header";
var PageHeaderSchema = {
	title: "Derico Page Header",
	fieldsets: [{
		id: "default",
		title: "Default",
		fields: ["kicker"]
	}],
	required: [],
	properties: { kicker: {
		title: "Kicker",
		description: "The line above the title. The title and the description are the page’s own fields — type them on the canvas."
	} }
};
//#endregion
//#region src/pageheader/index.tsx
function installDericoPageHeader(config) {
	config.blocks.blocksConfig[PAGE_HEADER_BLOCK_TYPE] = {
		id: PAGE_HEADER_BLOCK_TYPE,
		title: "Derico Page Header",
		icon: PageHeaderIcon,
		edit: PageHeaderEdit,
		view: PageHeaderView,
		blockSchema: PageHeaderSchema,
		defaultBlockWidth: "layout"
	};
	return config;
}
//#endregion
export { PAGE_HEADER_BLOCK_TYPE, installDericoPageHeader as default };

//# sourceMappingURL=pageheader.js.map