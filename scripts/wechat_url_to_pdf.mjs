#!/usr/bin/env node
/**
 * Capture a single WeChat Official Account article URL as PDF.
 *
 * This intentionally avoids external npm dependencies. It launches the local
 * Google Chrome app with a temporary profile, controls it through the Chrome
 * DevTools Protocol, scrolls the page to trigger lazy images, rewrites common
 * WeChat lazy-image attributes, then prints the fully rendered article to PDF.
 */

import { spawn } from "node:child_process";
import { mkdir, mkdtemp, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { tmpdir } from "node:os";
import { basename, join, resolve } from "node:path";

const DEFAULT_CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";

function usage() {
  console.log(`Usage:
  node scripts/wechat_url_to_pdf.mjs "https://mp.weixin.qq.com/s/..." --out-dir path/to/output

Options:
  --out-dir DIR              Output directory. Default: ./wechat-url-capture
  --pdf NAME                 PDF filename. Default: source.pdf
  --html NAME                HTML filename. Default: source.html
  --screenshot NAME          Screenshot filename. Default: fullpage.png
  --report NAME              Report filename. Default: capture-report.json
  --chrome PATH              Chrome executable path.
  --headed                   Show browser window instead of headless mode.
  --wait-ms N                Extra wait after scrolling. Default: 1500
  --scroll-step N            Scroll step in px. Default: 650
  --scroll-wait-ms N         Wait per scroll step. Default: 350
  --timeout-ms N             Navigation timeout. Default: 45000
  --allow-missing-images     Exit 0 even if some images failed to load.
  --help                     Show this help.

Outputs:
  source.pdf, source.html, fullpage.png, capture-report.json
`);
}

function parseArgs(argv) {
  const args = {
    url: null,
    outDir: "wechat-url-capture",
    pdf: "source.pdf",
    html: "source.html",
    screenshot: "fullpage.png",
    report: "capture-report.json",
    chrome: DEFAULT_CHROME,
    headed: false,
    waitMs: 1500,
    scrollStep: 650,
    scrollWaitMs: 350,
    timeoutMs: 45000,
    allowMissingImages: false,
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--help" || arg === "-h") {
      usage();
      process.exit(0);
    } else if (arg === "--out-dir") {
      args.outDir = argv[++i];
    } else if (arg === "--pdf") {
      args.pdf = argv[++i];
    } else if (arg === "--html") {
      args.html = argv[++i];
    } else if (arg === "--screenshot") {
      args.screenshot = argv[++i];
    } else if (arg === "--report") {
      args.report = argv[++i];
    } else if (arg === "--chrome") {
      args.chrome = argv[++i];
    } else if (arg === "--headed") {
      args.headed = true;
    } else if (arg === "--wait-ms") {
      args.waitMs = Number(argv[++i]);
    } else if (arg === "--scroll-step") {
      args.scrollStep = Number(argv[++i]);
    } else if (arg === "--scroll-wait-ms") {
      args.scrollWaitMs = Number(argv[++i]);
    } else if (arg === "--timeout-ms") {
      args.timeoutMs = Number(argv[++i]);
    } else if (arg === "--allow-missing-images") {
      args.allowMissingImages = true;
    } else if (!args.url) {
      args.url = arg;
    } else {
      throw new Error(`Unknown argument: ${arg}`);
    }
  }

  if (!args.url) {
    usage();
    throw new Error("Missing WeChat article URL");
  }
  if (!/^https?:\/\//.test(args.url)) {
    throw new Error(`URL must start with http:// or https://: ${args.url}`);
  }
  if (!existsSync(args.chrome)) {
    throw new Error(`Chrome executable not found: ${args.chrome}`);
  }
  return args;
}

async function sleep(ms) {
  await new Promise((resolveSleep) => setTimeout(resolveSleep, ms));
}

async function waitForJson(url, timeoutMs) {
  const start = Date.now();
  let lastError;
  while (Date.now() - start < timeoutMs) {
    try {
      const response = await fetch(url);
      if (response.ok) return await response.json();
      lastError = new Error(`${response.status} ${response.statusText}`);
    } catch (error) {
      lastError = error;
    }
    await sleep(200);
  }
  throw new Error(`Timed out waiting for ${url}: ${lastError?.message || "unknown error"}`);
}

class CDP {
  constructor(wsUrl) {
    this.ws = new WebSocket(wsUrl);
    this.nextId = 1;
    this.pending = new Map();
    this.listeners = new Map();
  }

  async open() {
    await new Promise((resolveOpen, rejectOpen) => {
      this.ws.addEventListener("open", resolveOpen, { once: true });
      this.ws.addEventListener("error", rejectOpen, { once: true });
    });
    this.ws.addEventListener("message", (event) => {
      const message = JSON.parse(event.data);
      if (message.id && this.pending.has(message.id)) {
        const { resolveCommand, rejectCommand } = this.pending.get(message.id);
        this.pending.delete(message.id);
        if (message.error) rejectCommand(new Error(JSON.stringify(message.error)));
        else resolveCommand(message.result || {});
        return;
      }
      if (message.method && this.listeners.has(message.method)) {
        for (const listener of this.listeners.get(message.method)) listener(message.params || {});
      }
    });
  }

  send(method, params = {}) {
    const id = this.nextId++;
    const payload = JSON.stringify({ id, method, params });
    return new Promise((resolveCommand, rejectCommand) => {
      this.pending.set(id, { resolveCommand, rejectCommand });
      this.ws.send(payload);
    });
  }

  once(method, timeoutMs = 30000) {
    return new Promise((resolveEvent, rejectEvent) => {
      const timer = setTimeout(() => {
        cleanup();
        rejectEvent(new Error(`Timed out waiting for event ${method}`));
      }, timeoutMs);
      const listener = (params) => {
        cleanup();
        resolveEvent(params);
      };
      const cleanup = () => {
        clearTimeout(timer);
        const listeners = this.listeners.get(method) || [];
        this.listeners.set(
          method,
          listeners.filter((item) => item !== listener),
        );
      };
      if (!this.listeners.has(method)) this.listeners.set(method, []);
      this.listeners.get(method).push(listener);
    });
  }

  close() {
    this.ws.close();
  }
}

async function launchChrome(args, port, userDataDir) {
  const chromeArgs = [
    `--remote-debugging-port=${port}`,
    `--user-data-dir=${userDataDir}`,
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-background-networking",
    "--disable-sync",
    "--disable-extensions",
    "--disable-popup-blocking",
    "--hide-scrollbars",
    "about:blank",
  ];
  if (!args.headed) chromeArgs.unshift("--headless=new");

  const proc = spawn(args.chrome, chromeArgs, {
    stdio: ["ignore", "pipe", "pipe"],
  });
  let stderr = "";
  proc.stderr.on("data", (chunk) => {
    stderr += chunk.toString();
  });
  proc.on("exit", (code) => {
    if (code && code !== 0) {
      console.error(stderr.trim());
    }
  });
  return proc;
}

async function terminateChrome(proc) {
  if (!proc || proc.exitCode !== null) return;
  const exited = new Promise((resolveExit) => {
    proc.once("exit", resolveExit);
  });
  proc.kill("SIGTERM");
  const graceful = await Promise.race([
    exited.then(() => true),
    sleep(2000).then(() => false),
  ]);
  if (!graceful && proc.exitCode === null) {
    proc.kill("SIGKILL");
    await Promise.race([exited, sleep(1000)]);
  }
}

async function getPageWebSocket(port, timeoutMs) {
  const list = await waitForJson(`http://127.0.0.1:${port}/json/list`, timeoutMs);
  const page = list.find((item) => item.type === "page");
  if (!page?.webSocketDebuggerUrl) {
    throw new Error("Could not find Chrome page websocket");
  }
  return page.webSocketDebuggerUrl;
}

async function evaluate(cdp, expression, awaitPromise = true) {
  const result = await cdp.send("Runtime.evaluate", {
    expression,
    awaitPromise,
    returnByValue: true,
  });
  if (result.exceptionDetails) {
    throw new Error(JSON.stringify(result.exceptionDetails));
  }
  return result.result?.value;
}

function lazyLoadExpression({ scrollStep, scrollWaitMs, waitMs }) {
  return `;(async () => {
    const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
    const sourceAttrs = [
      'data-src',
      'data-original',
      'data-backsrc',
      'data-w',
      'data-copyrightwatermarksrc',
      'data-ratio-src'
    ];
    function patchImages() {
      for (const img of Array.from(document.images)) {
        const current = img.getAttribute('src') || '';
        const shouldReplace = !current || current.startsWith('data:') || current === 'about:blank';
        const candidate = sourceAttrs.map((attr) => img.getAttribute(attr)).find(Boolean);
        if (candidate && shouldReplace) img.setAttribute('src', candidate);
        img.removeAttribute('loading');
        img.style.maxWidth = '100%';
        img.style.height = 'auto';
      }
    }
    patchImages();
    let lastHeight = 0;
    let stableRounds = 0;
    for (let y = 0; y <= Math.max(document.body.scrollHeight, document.documentElement.scrollHeight); y += ${scrollStep}) {
      window.scrollTo(0, y);
      patchImages();
      await sleep(${scrollWaitMs});
      const height = Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);
      if (height === lastHeight) stableRounds += 1;
      else stableRounds = 0;
      lastHeight = height;
      if (stableRounds > 6 && y > height - window.innerHeight) break;
    }
    window.scrollTo(0, Math.max(document.body.scrollHeight, document.documentElement.scrollHeight));
    patchImages();
    await sleep(${waitMs});
    window.scrollTo(0, 0);
    await Promise.all(Array.from(document.images).map((img) => new Promise((resolve) => {
      if (img.complete) return resolve();
      const done = () => resolve();
      img.addEventListener('load', done, { once: true });
      img.addEventListener('error', done, { once: true });
      setTimeout(done, 5000);
    })));
    patchImages();
    const articleRoot = document.querySelector('#js_content') || document.body;
    const allImages = Array.from(articleRoot.querySelectorAll('img'));
    const images = allImages.map((img, index) => {
      const src = img.currentSrc || img.src || '';
      const dataSrc = img.getAttribute('data-src') || '';
      const box = img.getBoundingClientRect();
      const hasCandidate = Boolean(src || dataSrc);
      const meaningful = hasCandidate && (box.width > 2 || box.height > 2 || img.naturalWidth > 0 || img.naturalHeight > 0);
      return {
      index,
      src,
      dataSrc,
      complete: img.complete,
      naturalWidth: img.naturalWidth,
      naturalHeight: img.naturalHeight,
      visibleWidth: Math.round(box.width),
      visibleHeight: Math.round(box.height),
      meaningful
    };
    });
    const meaningfulImages = images.filter((img) => img.meaningful);
    const failed = meaningfulImages.filter((img) => !img.complete || !img.naturalWidth || !img.naturalHeight);
    return {
      title: document.title,
      articleTitle: (document.querySelector('#activity-name')?.textContent || '').trim(),
      accountName: (document.querySelector('#js_name')?.textContent || '').trim(),
      publishTime: (document.querySelector('#publish_time')?.textContent || '').trim(),
      url: location.href,
      imageCount: meaningfulImages.length,
      rawImageCount: images.length,
      failedImageCount: failed.length,
      images: meaningfulImages,
      ignoredImageCount: images.length - meaningfulImages.length,
      bodyHeight: Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)
    };
  })()`;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const outDir = resolve(args.outDir);
  await mkdir(outDir, { recursive: true });

  const userDataDir = await mkdtemp(join(tmpdir(), "wechat-url-to-pdf-"));
  const port = 9333 + Math.floor(Math.random() * 1000);
  const chrome = await launchChrome(args, port, userDataDir);
  let cdp;

  try {
    const wsUrl = await getPageWebSocket(port, 10000);
    cdp = new CDP(wsUrl);
    await cdp.open();
    await cdp.send("Page.enable");
    await cdp.send("Runtime.enable");
    await cdp.send("Network.enable");
    await cdp.send("Emulation.setDeviceMetricsOverride", {
      width: 900,
      height: 1200,
      deviceScaleFactor: 1,
      mobile: false,
    });
    await cdp.send("Network.setUserAgentOverride", {
      userAgent:
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    });

    const loadEvent = cdp.once("Page.loadEventFired", args.timeoutMs);
    await cdp.send("Page.navigate", { url: args.url });
    await loadEvent;

    await evaluate(
      cdp,
      `new Promise((resolve) => {
        const start = Date.now();
        const tick = () => {
          if (document.querySelector('#js_content') || document.querySelector('#activity-name')) resolve(true);
          else if (Date.now() - start > ${args.timeoutMs}) resolve(false);
          else setTimeout(tick, 250);
        };
        tick();
      })`,
    );

    const loadReport = await evaluate(
      cdp,
      lazyLoadExpression({
        scrollStep: args.scrollStep,
        scrollWaitMs: args.scrollWaitMs,
        waitMs: args.waitMs,
      }),
    );

    await cdp.send("Page.addScriptToEvaluateOnNewDocument", { source: "" }).catch(() => {});
    await evaluate(
      cdp,
      `(() => {
        const style = document.createElement('style');
        style.textContent = \`
          @media print {
            body { background: #fff !important; }
            img { max-width: 100% !important; height: auto !important; page-break-inside: avoid; break-inside: avoid; }
            iframe, video, audio, .rich_media_tool, .qr_code_pc_outer, #js_pc_qr_code, #js_tags_preview_to_html, .reward_area, .comment_area, .profile_container { display: none !important; }
            #js_content { overflow: visible !important; }
          }
        \`;
        document.head.appendChild(style);
      })()`,
    );

    const html = await evaluate(cdp, "document.documentElement.outerHTML");
    await writeFile(join(outDir, args.html), html, "utf8");

    const screenshot = await cdp.send("Page.captureScreenshot", {
      format: "png",
      captureBeyondViewport: true,
      fromSurface: true,
    });
    await writeFile(join(outDir, args.screenshot), Buffer.from(screenshot.data, "base64"));

    const pdf = await cdp.send("Page.printToPDF", {
      printBackground: true,
      preferCSSPageSize: false,
      paperWidth: 8.27,
      paperHeight: 11.69,
      marginTop: 0.35,
      marginBottom: 0.35,
      marginLeft: 0.35,
      marginRight: 0.35,
      transferMode: "ReturnAsBase64",
    });
    await writeFile(join(outDir, args.pdf), Buffer.from(pdf.data, "base64"));

    const report = {
      capturedAt: new Date().toISOString(),
      inputUrl: args.url,
      outputDir: outDir,
      files: {
        pdf: join(outDir, args.pdf),
        html: join(outDir, args.html),
        screenshot: join(outDir, args.screenshot),
        report: join(outDir, args.report),
      },
      chrome: basename(args.chrome),
      headed: args.headed,
      ...loadReport,
      notes: [
        "PDF was generated from rendered Chrome output, not raw HTML.",
        "Images are patched from common WeChat lazy-load attributes and verified by naturalWidth/naturalHeight.",
        "If failedImageCount is nonzero, rerun with --headed or manually inspect the page.",
      ],
    };
    await writeFile(join(outDir, args.report), JSON.stringify(report, null, 2), "utf8");

    console.log(join(outDir, args.pdf));
    console.log(join(outDir, args.report));
    console.log(`images=${report.imageCount} failed=${report.failedImageCount}`);

    if (report.failedImageCount > 0 && !args.allowMissingImages) {
      process.exitCode = 2;
    }
  } finally {
    if (cdp) cdp.close();
    await terminateChrome(chrome);
  }
}

main().catch((error) => {
  console.error(`ERROR: ${error.message}`);
  process.exit(1);
});
