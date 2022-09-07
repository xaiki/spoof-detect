import PQueue from "https://deno.land/x/p_queue@1.0.1/mod.ts"

import * as CSV from './csv.ts';
import Puppet from './puppet.ts';
import selectors from './selectors.ts';

const puppet = new Puppet();
const queue = new PQueue({
  concurrency: 10,
  timeout: 60000
})
let count = 0
let statInterval
queue.addEventListener("active", () =>
  console.log(`Working on item #${++count}.  Size: ${queue.size}  Pending: ${queue.pending}`))
queue.addEventListener("next", () =>
  console.log(`task finished, Size: ${queue.size} Pending: ${queue.pending}`))

queue.addEventListener("idle", async () => {
  clearInterval(statInterval)
  await puppet.close()
  console.log("all done")
})

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


function process(o: { id: int, url: string, bco: string, name: string }): Promise<void> {
  const promises: Promise<void>[] = [];

  return puppet.run(async page => {
    const url = o.url.replace('http:', 'https:');
    promises.push(new Promise<void>((accept, _reject) => {
      page.once('load', async () => {
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
            console.log('got bb', o.bco, bb)

            try {
              await logos[i].screenshot({ path: `./data/logos/${o.bco}.logo${i}.png` })
              annotations +=
                `${o.id} ${bb.x + bb.width / 2} ${bb.y + bb.height / 2} ${bb.width} ${bb.height}\n`
            } catch (e) {
              console.error(`couldn't screenshot logo: ${e}`);
            }
          }
          if (logos.length) {
            await Deno.writeTextFile(`./data/${o.bco}.chrome.full.txt`, annotations);
          }
          await page.screenshot({ path: `./data/${o.bco}.chrome.full.png`, fullPage: true })
          console.log(`screenshot ok for ${o.name}`);
        } catch (err) {
          console.error(`error in screenshot: ${err}`);
        }
        accept()
      })
    }))

    try {
      await page.goto(url)
        .catch(() => page.goto(o.url))
    } catch (e) {
      console.error(`got error: ${e}`);
    }
    await Promise.all(promises);
  })
}

async function run() {
  let text;
  try {
    text = await Deno.readTextFile("./data/entities.csv")
  } catch (e) {
    console.error(`couldn't read csv: ${e}`)
  }
  if (!text) return setTimeout(run, 1000)
  statInterval = setInterval(() =>
    console.log(`Size: ${queue.size}  Pending: ${queue.pending}`), 1000);

  CSV.parse(text, o => queue.add(() => process(o)))
}
run()
