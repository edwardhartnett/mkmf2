import os
import sys
import pdb; pdb.set_trace()

for folder, subs, files in os.walk('.'):
    if folder[0:6] != './.git':
        for filename in files:
            print filename
            # with open(os.path.join(folder, filename), 'r') as src:
            #     dest.write(src.read())
