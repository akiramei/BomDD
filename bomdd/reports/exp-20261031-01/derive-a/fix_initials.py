import json
p = 'domain-model.json'
m = json.load(open(p, encoding='utf-8'))
fix = {('ExportRequest', 'clip'): '依頼を作る側が与える',
       ('ExportRequest', 'document'): '依頼を作る側が与える(書き出し時点の Document)',
       ('KeyframeLookup', 'target'): '呼び出し側が与える(スパンの開始)',
       ('ExportJob', 'outcome'): '書き出しの終了で決まる(終了前は値なし)',
       ('ExportJob', 'exitCode'): 'FfmpegFailed のときだけ値を持つ',
       ('ExportJob', 'errorTail'): 'FfmpegFailed のときだけ値を持つ'}
for e in m['entities']:
    for a in e['attributes']:
        k = (e['name'], a['name'])
        if k in fix:
            a['initial'] = fix[k]
unk = [f"{e['name']}.{a['name']}" for e in m['entities'] for a in e['attributes'] if a['initial'] == 'unknown']
print(unk)
with open(p, 'w', encoding='utf-8') as f:
    json.dump(m, f, ensure_ascii=False, indent=2)
