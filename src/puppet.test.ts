import { assertEquals } from "https://deno.land/std@0.152.0/testing/asserts.ts";
import Puppet from './puppet.ts'

Deno.test("Puppet", async () => {
  const P = new Puppet()
  await P.connect()
  await P.run(page => page.goto("https://google.com"))
  await P.close()
})
