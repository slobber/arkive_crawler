import json
SIZE = 1000
with open('arkive.json', encoding='utf-8') as f:
    j = json.load(f)
    data = j["response"]["docs"]
    data = sorted(data, key=lambda k: k['id'])

    result = []
    for i in range(0, len(data), SIZE):
        result.append(data[i:i+SIZE])

    i = 0
    for sp in result:
        with open('data/arkive_{}.json'.format(i), 'w', encoding='utf-8') as ff:
            j["response"]["docs"] = sp
            json.dump(j, ff)
        i = i + 1
