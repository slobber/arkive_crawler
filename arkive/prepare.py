import errno
import json
import os


OUTPUT_ROOT = os.path.join(os.getcwd(), 'output')


def load():
    with open('index', encoding='utf-8') as i:
        index = i.readline()

    all_spices_url = []
    data = {}
    with open('data/arkive_{}.json'.format(index), encoding='utf-8') as f:
        spices = json.load(f)["response"]["docs"]

        for spice in spices:
            data[spice['id'][:-1]] = spice
            all_spices_url.append('https://www.arkive.org/' + spice['id'] + 'factsheet')

    with open('index', 'w', encoding='utf-8') as i:
        i.write(str(int(index) + 1))

    return all_spices_url, data


# all_spices_url, data = load()


if __name__ == 'main':
    load()
