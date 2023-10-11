import selectors from './selectors.ts';

export async function get_logos(page, selector): {}[] {
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

export async function fetch_logos(page, dest) {
    console.error(`getting logos for: ${dest}`)
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
            console.log('got bb', bb)

            try {
                await logos[i].screenshot({
                    path: dest
                        .replace('images', 'logos')
                        .replace('.png', `.${i}.png`)
                })
                annotations +=
                    `${o.id} ${bb.x + bb.width / 2} ${bb.y + bb.height / 2} ${bb.width} ${bb.height}\n`
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
