from pymongo import MongoClient
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

client = MongoClient()
db = client.neutron_stars
collection = db.N10K_r26_Z02_1

single_neutron_stars = []
binary_neutron_stars = []
escapes = []

for star in collection.find():
    for timestep in star['data']:
        if timestep['type'] == 13:
            if timestep['binary']:
                binary_neutron_stars.append(timestep['time'])
            else:
                single_neutron_stars.append(timestep['time'])

    if star['escape']:
        if star['data'][-1]['type'] == 13:
            escapes.append(star['escape'])

bins = 50
_, bins_singles, _ = plt.hist(single_neutron_stars, bins)
_, bins_binaries, _ = plt.hist(binary_neutron_stars, bins)
_, bins_escapes, _ = plt.hist(escapes, bins)
plt.clf()

max_bin = max([bins_singles[-1], bins_binaries[-1], bins_escapes[-1]])
if max_bin == bins_singles[-1]:
    bins = bins_singles
elif max_bin == bins_binaries[-1]:
    bins = bins_binaries
elif max_bin == bins_escapes[-1]:
    bins = bins_escapes

plt.hist(single_neutron_stars, bins, label='singles')
plt.hist(binary_neutron_stars, bins, label='binary')
plt.hist(escapes, bins, label='escapes')
plt.legend()
plt.savefig('test_run.png')
