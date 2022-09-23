import Puppeteer from "https://deno.land/x/puppeteer@16.2.0/mod.ts";
import EventEmitter from "https://deno.land/x/events@v1.0.0/mod.ts";
import type { Browser, Page } from "https://deno.land/x/puppeteer@16.2.0/mod.ts";

const BROWSER_SIGNALS = [
    'disconnected',
    'targetchanged',
    'targetcreated',
    'targetdestroyed'
];

const CHROME_ARGS = [
    '--no-sandbox',
    '--disable-setuid-sandbox'
];

async function resolve(q: string) {
    if (q.match(/(\d.?){4}/)) {
        return q;
    }
    return await Deno.resolveDns(q, "A");
}

export default class Runner extends EventEmitter {
    config: {
        BROWSERLESS_HOST: string;
        BROWSERLESS_PORT: string;
    };
    target: string;
    browser: Browser | undefined;
    connected: Promise<boolean> | undefined;

    constructor(config = {
        BROWSERLESS_HOST: Deno.env.get("BROWSERLESS_HOST") || "localhost",
        BROWSERLESS_PORT: Deno.env.get("BROWSERLESS_PORT") || "3000",
    }) {
        super();
        this.target = `ws://${config.BROWSERLESS_HOST}:${config.BROWSERLESS_PORT}`;
        this.config = config;
        this.connected
    }
    public async close() {
        try {
            if (this.browser) await this.browser.close();
        } catch (err) {
            console.error(`${err} on close`)
        }
    }
    async connect() {
        if (!this.connected)
            this.connected = this._connect()
        return this.connected
    }
    async _connect() {
        try {
            const host = await resolve(this.config.BROWSERLESS_HOST);
            const ver = await fetch(`http://${host}:${this.config.BROWSERLESS_PORT}/json/version`)
                .then(async res => await res.json())
            this.target = ver.webSocketDebuggerUrl;
            this.browser = this.browser || await Puppeteer.connect({
                browserWSEndpoint: this.target
            }).catch(() => {
                console.error(`
⚠ COULD NOT CONNECT TO BROWSERLESS
🦄 will try to spawn a chromedriver instance for you to debug`)
                return Puppeteer.launch({
                    args: CHROME_ARGS,
                    headless: false
                })
            });

            if (!this.browser) {
                console.error("couldn't init Browser");
                return false;
            }
            BROWSER_SIGNALS.map(e => this.browser?.on(e, d => this.emit(`browser:${e}`, d)))
            this.browser.on('error', e => console.error(`got browser error: ${e}`))

            const pages = await this.browser.pages();
            for (let p in pages) {
                await pages[p].close();
            }
            this.emit("ready")
        } catch (e) {
            console.error(e);
        }
        return true;
    }

    public async run(fn: (page: Page) => void) {
        await this.connect();

        if (!this.browser) {
            return;
        }
        try {
            const page = await this.browser.newPage()
            if (!page) {
                return;
            }
            const ret = await fn(page)
            await page.close()
            return ret
        } catch (e) {
            return
        }
    }
}
