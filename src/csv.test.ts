import {
  assertEquals,
  assertObjectMatch
} from "https://deno.land/std@0.152.0/testing/asserts.ts";
import * as CSV from './csv.ts';

Deno.test("ParseLine", () => {
  assertEquals(CSV.parseLine('"test", "test, with", without'), ['test', 'test, with', 'without'])
})
Deno.test("ParseCSV", () => {
  const res: object[] = []
  const expected = { test: 'hello', case: 'world' }
  CSV.parse('test,case\nhello,world', e => res.push(e))
  assertObjectMatch(res[0], expected)
  assertEquals(res, [expected])
})
