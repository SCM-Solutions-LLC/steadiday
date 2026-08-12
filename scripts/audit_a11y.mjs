#!/usr/bin/env node
/**
 * Accessibility audit for the SteadiDay site.
 *
 * Three layers, because no single one of them is sufficient:
 *
 * 1. Contrast, measured against *computed* styles in a real browser rather
 *    than by reading CSS. It resolves custom properties, walks up for the
 *    effective background, picks the worst stop of a gradient, and composites
 *    semi-transparent text. Several real failures here were invisible to
 *    static analysis.
 *
 * 2. axe-core, for the things a bespoke check has no business reimplementing:
 *    ARIA validity, accessible names, landmark and heading structure, form
 *    labels, list and table semantics. Its own color-contrast rule is disabled
 *    because layer 1 is stricter about gradients and alpha, and running both
 *    just double-reports the same pixels.
 *
 * 3. A keyboard pass, which axe cannot do because it is static: it tabs
 *    through the page looking for keyboard traps, tab order that diverges
 *    from DOM order, and focused elements with no visible focus indicator.
 *
 * Needs a server already running at BASE_URL. `scripts/audit.sh` starts one,
 * installs the two dependencies if they are missing, and is the easier way in:
 *
 *   scripts/audit.sh                             # audit everything
 *   scripts/audit.sh index.html pricing.html     # audit specific pages
 *   node scripts/audit_a11y.mjs                  # if a server is already up
 *
 * Env:
 *   BASE_URL        default http://localhost:8899
 *   CHROMIUM_PATH   explicit browser binary; otherwise auto-discovered
 *   SKIP_AXE=1      skip layer 2 (useful when iterating on layers 1 and 3)
 *
 * Exits non-zero if anything fails.
 */

import { readdirSync, existsSync } from "node:fs";
import { join } from "node:path";
import { createRequire as makeRequire } from "node:module";

const BASE_URL = process.env.BASE_URL || "http://localhost:8899";
const require = makeRequire(import.meta.url);

function axeSourcePath() {
  try {
    return require.resolve("axe-core");
  } catch {
    return null;
  }
}

async function loadChromium() {
  for (const mod of ["playwright", "playwright-core"]) {
    try {
      return (await import(mod)).chromium;
    } catch {
      /* try the next one */
    }
  }
  throw new Error("Install `playwright` or `playwright-core` to run this audit.");
}

/**
 * Locate a Chromium binary.
 *
 * Returns null when Playwright already knows where its own download is, which
 * is the normal case in CI after `npx playwright install`. The fallback exists
 * for environments that ship a browser but no Playwright download - notably
 * `playwright-core`, which never downloads one - where launching without an
 * explicit path fails with "executable doesn't exist".
 */
function findChromium(chromium) {
  if (process.env.CHROMIUM_PATH) return process.env.CHROMIUM_PATH;

  try {
    const bundled = chromium.executablePath();
    if (bundled && existsSync(bundled)) return null;
  } catch {
    /* playwright-core throws here rather than returning a path */
  }

  const roots = [process.env.PLAYWRIGHT_BROWSERS_PATH, "/opt/pw-browsers"].filter(Boolean);
  for (const root of roots) {
    if (!existsSync(root)) continue;
    // Prefer headless_shell: it is smaller and this audit never needs a head.
    for (const leaf of ["chrome-linux/headless_shell", "chrome-linux/chrome"]) {
      const hit = readdirSync(root)
        .filter((d) => d.startsWith("chromium"))
        .sort()
        .reverse()
        .map((d) => join(root, d, leaf))
        .find(existsSync);
      if (hit) return hit;
    }
  }
  return null;
}

function discoverPages() {
  const pages = readdirSync(".").filter((f) => f.endsWith(".html")).sort();
  if (existsSync("blog")) {
    for (const f of readdirSync("blog").sort()) {
      if (f.endsWith(".html")) pages.push(join("blog", f));
    }
  }
  return pages;
}

/**
 * Runs inside the page. Kept as one function so it can be serialised.
 * Returns contrast failures plus the structural checks.
 */
function auditInPage() {
  const chan = (c) => {
    c /= 255;
    return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
  };
  const lum = ([r, g, b]) => 0.2126 * chan(r) + 0.7152 * chan(g) + 0.0722 * chan(b);
  const ratio = (a, b) => {
    const l1 = lum(a), l2 = lum(b);
    return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
  };
  const nums = (s) => (s.match(/[\d.]+/g) || []).map(Number);
  const alphaOf = (s) => {
    const m = s.match(/rgba\([^)]*,\s*([\d.]+)\s*\)/);
    return m ? parseFloat(m[1]) : 1;
  };
  const composite = (fg, a, bg) => fg.map((c, i) => Math.round(c * a + bg[i] * (1 - a)));

  // Candidate backgrounds behind an element. Only opaque colours count: a
  // 0.13-alpha tint or a `transparent` gradient stop does not determine the
  // effective backdrop, so keep walking up the tree.
  function backgrounds(el) {
    let n = el;
    while (n && n !== document.documentElement) {
      const cs = getComputedStyle(n);
      const bi = cs.backgroundImage;
      if (bi && bi !== "none") {
        const stops = [...bi.matchAll(/rgba?\(([^)]+)\)/g)]
          .map((m) => nums(m[1]))
          .filter((v) => v.length < 4 || v[3] > 0.85)
          .map((v) => v.slice(0, 3));
        if (stops.length) return stops;
      }
      const bc = cs.backgroundColor;
      if (bc && alphaOf(bc) > 0.85) return [nums(bc).slice(0, 3)];
      n = n.parentElement;
    }
    return [[255, 255, 255]];
  }

  // Decorative content is exempt from contrast requirements.
  function ariaHidden(el) {
    for (let n = el; n; n = n.parentElement) {
      if (n.getAttribute && n.getAttribute("aria-hidden") === "true") return true;
    }
    return false;
  }

  const failures = [];
  for (const el of document.querySelectorAll("body *")) {
    const text = [...el.childNodes]
      .filter((n) => n.nodeType === 3)
      .map((n) => n.textContent.trim())
      .join("");
    if (!text || ariaHidden(el)) continue;

    const cs = getComputedStyle(el);
    if (cs.visibility === "hidden" || cs.display === "none" || parseFloat(cs.opacity) === 0) continue;
    const box = el.getBoundingClientRect();
    if (!box.width || !box.height) continue;

    const fg = nums(cs.color).slice(0, 3);
    if (fg.length < 3) continue;
    const fgAlpha = alphaOf(cs.color);

    const size = parseFloat(cs.fontSize);
    const weight = parseInt(cs.fontWeight) || 400;
    const isLarge = size >= 24 || (size >= 18.66 && weight >= 700);
    const required = isLarge ? 3.0 : 4.5;

    let worst = Infinity, worstBg = null;
    for (const bg of backgrounds(el)) {
      const effective = fgAlpha < 1 ? composite(fg, fgAlpha, bg) : fg;
      const r = ratio(effective, bg);
      if (r < worst) { worst = r; worstBg = bg; }
    }
    if (worst < required) {
      failures.push({
        text: text.slice(0, 50),
        ratio: Math.round(worst * 100) / 100,
        required,
        size: Math.round(size * 10) / 10,
        fg: cs.color,
        bg: `rgb(${worstBg})`,
      });
    }
  }

  return {
    failures,
    skipLink: !!document.querySelector(".skip-link"),
    main: !!document.querySelector("main"),
    imagesWithoutAlt: [...document.images].filter((i) => !i.hasAttribute("alt")).length,
  };
}

/**
 * Tab through the page and report keyboard problems.
 *
 * axe is a static analyser: it can flag a positive tabindex, but it cannot
 * tell you whether focus actually moves, whether it moves in a sensible
 * order, or whether you can see where it went. That needs real key presses.
 */
async function keyboardPass(tab, maxStops = 60) {
  const problems = [];

  const describe = () =>
    tab.evaluate(() => {
      const el = document.activeElement;
      if (!el || el === document.body) return null;
      const cs = getComputedStyle(el);
      const outlineWidth = parseFloat(cs.outlineWidth) || 0;
      const hasRing =
        (outlineWidth > 0 && cs.outlineStyle !== "none") ||
        (cs.boxShadow && cs.boxShadow !== "none");
      // Position in document order, for detecting tab order that jumps around.
      const all = [...document.querySelectorAll("*")];
      return {
        tag: el.tagName.toLowerCase(),
        label: (el.getAttribute("aria-label") || el.textContent || "").trim().slice(0, 40),
        docIndex: all.indexOf(el),
        tabindex: el.getAttribute("tabindex"),
        hasRing,
        hidden: cs.visibility === "hidden" || cs.display === "none",
        offscreen: el.getBoundingClientRect().bottom < 0,
      };
    });

  // Settle transitions before measuring. Elements with `transition: all`
  // animate outline-width from 0 to its final value, so sampling the computed
  // style straight after a Tab reports "no focus ring" on a ring that is
  // simply still fading in. Zeroing durations is faster and more reliable
  // than sleeping after every key press.
  await tab.addStyleTag({
    content:
      "*, *::before, *::after { transition-duration: 0s !important; " +
      "animation-duration: 0s !important; }",
  });

  await tab.evaluate(() => {
    window.scrollTo(0, 0);
    document.body.focus();
  });

  const seen = [];
  let previous = null;
  let repeats = 0;

  for (let i = 0; i < maxStops; i++) {
    await tab.keyboard.press("Tab");
    const current = await describe();
    if (!current) break; // focus left the document

    const key = `${current.tag}:${current.docIndex}`;
    if (previous && key === previous) {
      repeats += 1;
      if (repeats >= 2) {
        problems.push(`keyboard trap: focus stuck on <${current.tag}> "${current.label}"`);
        break;
      }
    } else {
      repeats = 0;
    }
    previous = key;

    if (seen.some((s) => s.key === key)) break; // wrapped around
    seen.push({ key, ...current });
  }

  for (const stop of seen) {
    if (stop.tabindex && Number(stop.tabindex) > 0) {
      problems.push(
        `positive tabindex="${stop.tabindex}" on <${stop.tag}> "${stop.label}" ` +
          `overrides natural order`
      );
    }
    if (stop.hidden) {
      problems.push(`focusable but hidden: <${stop.tag}> "${stop.label}"`);
    }
    // Tabbing to an <iframe> moves focus into the embedded document, which
    // draws its own indicator and which the parent page cannot style. The
    // outer element never matches :focus, so requiring a ring on it would be
    // a permanent false positive.
    if (!stop.hasRing && stop.tag !== "iframe") {
      problems.push(`no visible focus indicator on <${stop.tag}> "${stop.label}"`);
    }
  }

  // Tab order should follow document order. The skip link is deliberately
  // first, so compare from the second stop onward.
  for (let i = 2; i < seen.length; i++) {
    if (seen[i].docIndex < seen[i - 1].docIndex) {
      problems.push(
        `tab order diverges from DOM order: <${seen[i].tag}> "${seen[i].label}" ` +
          `comes after <${seen[i - 1].tag}> "${seen[i - 1].label}" when tabbing, ` +
          `but before it in the document`
      );
      break; // one report is enough; they cascade
    }
  }

  return { problems, stops: seen.length };
}

const chromium = await loadChromium();
const pages = process.argv.slice(2).length ? process.argv.slice(2) : discoverPages();
const AXE_PATH = process.env.SKIP_AXE ? null : axeSourcePath();

if (!process.env.SKIP_AXE && !AXE_PATH) {
  console.log("note: axe-core is not installed, skipping rule checks (npm install axe-core)");
}

const executablePath = findChromium(chromium);
const browser = await chromium.launch(executablePath ? { executablePath } : {});

let totalFailures = 0;
const problemPages = [];

for (const page of pages) {
  const tab = await browser.newPage({ viewport: { width: 1440, height: 900 } });

  // Hermetic: third-party fonts, images and analytics cannot affect computed
  // colours, and blocking them keeps the audit fast and deterministic in CI.
  await tab.route("**/*", (route) => {
    const url = route.request().url();
    return url.startsWith(BASE_URL) ? route.continue() : route.abort();
  });

  const jsErrors = [];
  tab.on("pageerror", (e) => jsErrors.push(e.message));

  let report, axeViolations = [], keyboard = { problems: [], stops: 0 };
  try {
    await tab.goto(`${BASE_URL}/${page}`, { waitUntil: "domcontentloaded", timeout: 30000 });
    await tab.waitForTimeout(250);
    report = await tab.evaluate(auditInPage);

    if (AXE_PATH) {
      // Injected from disk, so it does not need a network request and is not
      // affected by the route blocking above.
      await tab.addScriptTag({ path: AXE_PATH });
      const axeResult = await tab.evaluate(async () => {
        const res = await window.axe.run(document, {
          runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"] },
          // Layer 1 owns contrast and handles gradients and alpha better.
          rules: { "color-contrast": { enabled: false } },
          resultTypes: ["violations"],
        });
        return res.violations.map((v) => ({
          id: v.id,
          impact: v.impact,
          help: v.help,
          nodes: v.nodes.slice(0, 3).map((n) => n.html.slice(0, 110)),
          count: v.nodes.length,
        }));
      });
      axeViolations = axeResult;
    }

    keyboard = await keyboardPass(tab);
  } catch (err) {
    console.log(`\n✗ ${page}\n    could not audit: ${err.message}`);
    problemPages.push(page);
    totalFailures += 1;
    await tab.close();
    continue;
  }

  const structural = [];
  if (!report.skipLink) structural.push("no .skip-link");
  if (!report.main) structural.push("no <main> landmark");
  if (report.imagesWithoutAlt) structural.push(`${report.imagesWithoutAlt} image(s) without alt`);
  if (jsErrors.length) structural.push(`JS error: ${jsErrors[0]}`);

  const axeCount = axeViolations.reduce((n, v) => n + v.count, 0);
  const bad =
    report.failures.length + structural.length + axeCount + keyboard.problems.length;
  totalFailures += bad;

  if (bad) {
    problemPages.push(page);
    console.log(`\n✗ ${page}`);
    for (const s of structural) console.log(`    ${s}`);
    for (const f of report.failures) {
      console.log(
        `    contrast ${f.ratio}:1 (needs ${f.required}) ${f.size}px "${f.text}"\n` +
          `        ${f.fg} on ${f.bg}`
      );
    }
    for (const v of axeViolations) {
      console.log(`    axe/${v.id} [${v.impact}] ${v.help} (${v.count} node(s))`);
      for (const n of v.nodes) console.log(`        ${n}`);
    }
    for (const k of keyboard.problems) console.log(`    keyboard: ${k}`);
  }
  await tab.close();
}

await browser.close();

console.log(`\naudited ${pages.length} page(s)`);
if (totalFailures) {
  console.log(`FAILED: ${totalFailures} problem(s) across ${problemPages.length} page(s)`);
  process.exit(1);
}
console.log("PASSED: no contrast or structural failures");
