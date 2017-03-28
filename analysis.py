from pymongo import MongoClient
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def plot_collection(db, collection_name):
    collection = db[collection_name]
    single_neutron_stars = []
    binary_neutron_stars = []
    escapes = []

    for star in collection.find():
        for timestep in star['data']:
            # If the star at this time is a neutron star
            if timestep['type'] == 13:
                # Append that time to the appropriate list
                if timestep['binary']:
                    binary_neutron_stars.append(timestep['time'])
                else:
                    single_neutron_stars.append(timestep['time'])

        # If the star escapes before the simulation ends
        if star['escape']:
            # And the star is a neutron star when it escapes
            if star['data'][-1]['type'] == 13:
                # Append the escape time to the escape list
                escapes.append(star['escape'])

    # Determine the largest bin range, which will be used as the bins for all
    # three.
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
    plt.title(collection_name)
    plt.xlabel('Time')
    plt.ylabel('Neutron Stars')
    plt.legend()
    plt.savefig('{0}.png'.format(collection_name))

def main():
    client = MongoClient()
    db = client.neutron_stars
    collection_name = 'N10K_r26_Z02_1'
    plot_collection(db, collection_name)

if __name__== "__main__":
    main()

