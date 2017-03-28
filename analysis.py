from pymongo import MongoClient
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def get_times(collection):
    """Gets the times where neutron stars existed.

    params:
        collection - a pymongo collection object
    returns:
        a tuple in the following format: (single neutron star times,
            binary neutron star times, escape times), where each
            element in the tuple is a list of times.
    """
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

    return (single_neutron_stars, binary_neutron_stars, escapes)

def plot_collection(db, collection_name):
    """Plots neutron star count histograms for one run.

    params:
        db - a pymongo db object
        collection_name - a string in a format such as
            N10K_r26_Z02_1
    """
    collection = db[collection_name]
    single_neutron_stars, binary_neutron_stars, escapes = get_times(collection)

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

def plot_simulation(db, collection_names, simulation_name):
    """Plots neutron star histograms for all runs.

    params:
        db - a pymongo db object
        collection_names - a list of strings in a format such as
            N10K_r26_Z02_1 or N10K_r26_Z02_13
        simulation_name - a string matching the collection names
            such as N10K_r26_Z02
    """
    # for each collection, get the singles, binaries, and escapes
    single_times = []
    binary_times = []
    escape_times = []
    for collection in collection_names:
        col_obj = db[collection]
        single_data, binary_data, escape_data = get_times(col_obj)
        single_times += single_data
        binary_times += binary_data
        escape_times += escape_data
        
    # Determine the largest bin range, which will be used as the bins for all
    # three.
    bins = 50
    _, bins_singles, _ = plt.hist(single_times, bins)
    _, bins_binaries, _ = plt.hist(binary_times, bins)
    _, bins_escapes, _ = plt.hist(escape_times, bins)
    plt.clf()

    max_bin = max([bins_singles[-1], bins_binaries[-1], bins_escapes[-1]])
    if max_bin == bins_singles[-1]:
        bins = bins_singles
    elif max_bin == bins_binaries[-1]:
        bins = bins_binaries
    elif max_bin == bins_escapes[-1]:
        bins = bins_escapes

    plt.hist(single_times, bins, label='singles')
    plt.hist(binary_times, bins, label='binary')
    plt.hist(escape_times, bins, label='escapes')
    plt.title(simulation_name)
    plt.xlabel('Time')
    plt.ylabel('Neutron Stars')
    plt.legend()
    plt.savefig('{0}.png'.format(simulation_name))

def test_plot_collection():
    client = MongoClient()
    db = client.neutron_stars
    collection_name = 'N10K_r26_Z02_1'
    plot_collection(db, collection_name)

def test_plot_simulation():
    client = MongoClient()
    db = client.neutron_stars

    simulation_name = 'N10K_r26_Z02'
    # Get collections that are runs of 'N10K_r26_Z02'
    runs = [x for x in db.collection_names() if len(x) > 13 and x[:13] == simulation_name + '_']
    plot_simulation(db, runs, simulation_name)

def main():
    test_plot_simulation()

if __name__== "__main__":
    main()

