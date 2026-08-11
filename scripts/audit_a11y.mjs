#!/usr/bin/env node
/**
 * Accessibility audit for the SteadiDay site.
 *
 * Checks every page against WCAG 2.1 AA contrast, plus the structural
 * invariants the site relies on (skip link, main landmark, image alt text).
 *
 * Contrast is measured against *computed* styles in a real browser rather than
 * by reading the CSS, which is what makes it trustworthy: it resolves CSS
 * custom properties, walks up for the effective background, picks the worst
 * stop of a gradient, and composites semi-transparent text over what is behind
 * it. Several real failures on this site were invisible to static analysis.
 *
 *   node scripts/audit_a11y.mjs                  # audit everything
 *   node scripts/audit_a11y.mjs index.html …     # audit specific pages
 *
 * Env:
 *   BASE_URL        default http://localhost:8899
 *   CHROMIUM_PATH   explicit browser binary (for playwright-core)
 *
 * Exits non-zero if anything fails.
 */

import { readdirSync, existsSync } from "node:fs";
import { join } from "node:path";

const BASE_URL = process.env.BASE_URL || "http://localhost:8899";

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

const chromium = await loadChromium();
const pages = process.argv.slice(2).length ? process.argv.slice(2) : discoverPages();

const launchOptions = process.env.CHROMIUM_PATH
  ? { executablePath: process.env.CHROMIUM_PATH }
  : {};
const browser = await chromium.launch(launchOptions);

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

  let report;
  try {
    await tab.goto(`${BASE_URL}/${page}`, { waitUntil: "domcontentloaded", timeout: 30000 });
    await tab.waitForTimeout(250);
    report = await tab.evaluate(auditInPage);
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

  const bad = report.failures.length + structural.length;
  totalFailures += bad;

  if (bad) {
    problemPages.push(page);
    console.log(`\n✗ ${page}`);
    for (const s of structural) console.log(`    ${s}`);
    for (const f of report.failures) {
      console.log(
        `    ${f.ratio}:1 (needs ${f.required}) ${f.size}px "${f.text}"\n` +
          `        ${f.fg} on ${f.bg}`
      );
    }
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
