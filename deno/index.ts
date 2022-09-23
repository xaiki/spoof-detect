import PQueue from "https://deno.land/x/p_queue@1.0.1/mod.ts"
import { Application, Router } from "https://deno.land/x/oak@v9.0.0/mod.ts";

import * as CSV from './csv.ts';
import Puppet from './puppet.ts';
import selectors from './selectors.ts';

const puppet = new Puppet();
async function get_logos(page, selector): {}[] {
  const logos = await page.$$(selector) || [];
  for (const i in logos) {
    const bb = await page.evaluate(e => {
      const { x, y, width, height } = e.getBoundingClientRect();
      return {
        x, y, width, height, top: window.screen.top, left: window.screen.left
      }
    }, logos[i])
    logos[i].box = bb;
  }
  return logos;
}

async function fetch_logos(page, id, dest) {
  console.error(`getting logos for: ${id}`)
        try {
          const imgs = await get_logos(page, selectors.img_logo);
          const ids = await get_logos(page, selectors.id_logo);
          const cls = await get_logos(page, selectors.class_logo);
          const logos = [
            ...imgs, ...ids, ...cls
          ]

          let annotations = '';
          for (const i in logos) {
            const bb = logos[i].box
            if (!bb
              || (bb.width < 10)
              || (bb.height < 10)
              || (bb.x + bb.width < 0)
              || (bb.y + bb.height < 0)) continue;
            console.log('got bb',  bb)

            try {
              await logos[i].screenshot({
                path: dest
                  .replace('images', 'logos')
                  .replace('.png', `.${i}.png`)
              })
              annotations +=
                `${id} ${bb.x + bb.width / 2} ${bb.y + bb.height / 2} ${bb.width} ${bb.height}\n`
            } catch (e) {
              console.error(`couldn't screenshot logo: ${e}`);
            }
          }
          if (logos.length) {
            await Deno.writeTextFile(dest
              .replace('images', 'labels')
              .replace('png', 'txt'),
                                     annotations);
        }
        } catch (err) {
          console.error(`error in screenshot: ${err}`);
        }
}

const app = new Application();
const router = new Router();

const stats = {
  in_flight: 0,
  done: 0
}
router.post('/screenshot', async (ctx) => {
  const {request, response} = ctx;
  const q = await request.body().value;

  stats.in_flight++;
  const ret = await puppet.run(async page => {
    console.error('running', q, stats)
    await page.goto(q.url, {waitUntil: 'networkidle2', timeout: 60000})
    await page.screenshot({ path: q.path, fullPage: true })
    if (q.logos) {
      await fetch_logos(page, q.id, q.logos)
    }
    console.error(`screenshot ok: ${q.path}`)
    return {response: 'ok'}
  })
  stats.in_flight--;
  stats.done++
  response.body = ret
})
router.post('/bco', async (ctx) => {
  const {request, response} = ctx;
  const q = await request.body().value;
  const ret = await process(q)

  console.error(`ret: ${ret}`)
  response.body = ret
});

app.use(router.routes())
app.use(router.allowedMethods())
const addr = '0.0.0.0:8000'
console.error(`listen on ${addr}`)
app.listen(addr)
