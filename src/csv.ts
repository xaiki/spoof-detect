export function parseLine(l: string) {
  const res = l.match(/((?:\s+"[^"]+")|(?:[^,"]+))/g) || [];
  for (let i = 0; i < res.length; i++) {
    res[i] = res[i].replace(/^\s+/, '').replace(/^"/, '').replace(/[\r\n"]+$/, '')
  }
  return res;
}

export function parse(t: string, cb: (o: object) => void) {
  const lines = t.split('\n');
  const header = parseLine(lines[0]);
  for (let i = 1; i < lines.length; i++) {
    if (!lines[i].length) {
      continue;
    }
    const l = parseLine(lines[i]) || []

    if (l.length < header.length) {
      console.error(`couldn't parse '${lines[i]}' yielded '${l}' of length ${l.length} expected ${header.length}: ${header}`);
      return null;
    }
    const e = { [header[0]]: l[0] };
    for (let j = 1; j < header.length; j++) {
      e[`${header[j]}`] = l[j];
    }
    cb(e)
  }
}
