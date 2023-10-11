router.post('/bco', async (ctx) => {
    const { request, response } = ctx;
    const q = await request.body().value;
    const ret = await process(q)

    console.error(`ret: ${ret}`)
    response.body = ret
})

function process(o: { id: int, url: string, bco: string, name: string }): Promise<void> {
    const promises: Promise<void>[] = [];

    return puppet.run(async page => {
        const url = o.url.replace('http:', 'https:');
        promises.push(new Promise<void>((accept, _reject) => {
            page.once('load', async () => {
                const dest = `./data/images/${e.bco}.chrome.full.png`
                await fetch_logos(page, bco.name, dest)
                await page.screenshot({ path: dest, fullPage: true })
                console.log(`screenshot ok for ${o.name}`);

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
