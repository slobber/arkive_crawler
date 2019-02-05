import sys
import os
import subprocess


if len(sys.argv) > 1:
    offset = int(sys.argv[1]) 
else:
    offset  = 0
    try:
        with open('index', encoding='utf-8') as f:
            offset = int(f.readline()) - 1
    except:
        pass
total = int(sys.argv[2]) if len(sys.argv) == 3 else len([name for name in os.listdir('data') if os.path.isfile(os.path.join('data', name))])
total = total + 1
with open('index', 'w', encoding='utf-8') as f:
    f.write(str(offset))

for i in range(offset, total):
    subprocess.run([sys.executable, '-m', 'scrapy', 'crawl', 'arkive'])
