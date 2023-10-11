import PQueue from "https://deno.land/x/p_queue@1.0.1/mod.ts"
import { Application, Router } from "https://deno.land/x/oak@v9.0.0/mod.ts";

import * as CSV from './csv.ts';
import Puppet from './puppet.ts';
import selectors from './selectors.ts';
import { fetch_logos } from './logos.ts';

const puppet = new Puppet();
const app = new Application();
const router = new Router();

const stats = {
  in_flight: 0,
  done: 0
}

export const DEFAULT_VIEWPORTS = [{
  width: 640,
  height: 480
}, {
  width: 1080,
  height: 800
}, {
  width: 640,
  height: 640
}, {
  width: 600,
  height: 800,
  hasTouch: true,
  isMobile: true
}]

router.post('/screenshot', async (ctx) => {
  const { request, response } = ctx;
  const { url, path = './debug.png', logos = false, viewports = DEFAULT_VIEWPORTS } = await request.body().value;

  stats.in_flight++;
  let i = 0, v = {};
  viewports.map(async (v, i) => {
    const ret = await puppet.run(async page => {
      await page.setViewport(v)
      console.error('running', url, stats, v)
      try {
        const npath = path.replace('.png', `.${i}.png`)

        await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 })
        await page.screenshot({ path: npath, fullPage: true })
        if (logos) {
          await fetch_logos(page, npath)
        }
        console.error(`screenshot ${v} / ${i} ok: ${path}`)
      } catch (e) {
        console.error(e)
      }
      return { response: 'ok' }
    })
  })
  stats.in_flight--;
  stats.done++
  response.body = { response: 'ok' }
})

app.use(router.routes())
app.use(router.allowedMethods())
const addr = '0.0.0.0:8000'
console.error(`listen on ${addr}`)
app.listen(addr)
