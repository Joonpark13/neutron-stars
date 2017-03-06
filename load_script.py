import os
import glob
from pymongo import MongoClient

NEUTRON_STAR = 13

def parse_sev(sev_name):
    """Takes in an sev file address and returns the physical time and a list of stars

    output format: {
        'time': float,
        'stars': [
            {
                'id': int,
                'type': int
            }, ...
        ]
    }
    """

    stars = []
    with open(sev_name, 'r') as f:
        row = f.readline().split()

        # Physical time is the second item in the first line
        physical_time = float(row[1])

        # Skip the header
        for _ in range(2):
            next(f)

        for line in f:
            data_line = line.split()
            if int(data_line[0]) == -1000: # -1000 is sentinel value indicating EOF
                return { "time": physical_time, "stars": stars }
            try:
                stars.append({ 'id': int(data_line[0]), 'type': int(data_line[1]) })
            # In case the sev file is incorrectly formatted
            except ValueError:
                print "Incorrectly formatted sev file detected. Ignoring incorrecty formatted data from:"
                print sev_name

    # This should only be required in case there is no -1000 EOF value
    return { "time": physical_time, "stars": stars }

def parse_save(save_dir, neutron_only = True):
    """Takes in a save directory address and returns a list of neutron stars.

    If neutron_only is False, return all stars
    data should be sorted by 'time'

    output format: [
        {
            'id': int,
            'data': [
                {
                    'time': float,
                    'type': int,
                }
            ]
        }, ...
    ]
    """
    files = os.path.join(save_dir, 'sev.83_*')

    stars = []
    for filename in glob.glob(files):
        sev_data = parse_sev(filename)
        for star in sev_data['stars']:
            if (neutron_only and star['type'] == NEUTRON_STAR) or (not neutron_only):
                matching_star = filter(lambda x: x['id'] == star['id'], stars)
                if matching_star:
                    matching_star[0]['data'].append({
                        'time': sev_data['time'],
                        'type': star['type']
                    })
                else:
                    stars.append({
                        'id': star['id'],
                        'data': [{
                            'time': sev_data['time'],
                            'type': star['type']
                        }]
                    })
    # Sort
    for star in stars:
        star['data'] = sorted(star['data'], key=lambda x: x['time'])

    return stars

def parse_run(run_dir, neutron_only = True):
    """Given a run directory address, returns a list of stars

    output format: [
        {
            'id': int,
            'data': [
                {
                    'time': float,
                    'type': int,
                }
            ]
        }, ...
    ]
    """
    files = os.path.join(run_dir, 'save0*')

    stars = []
    for save_dir in glob.glob(files):
        data = parse_save(save_dir, neutron_only)
        if len(stars) == 0:
            stars = data
        else:
            # Check for overlap
            for star in data:
                existing = filter(lambda x: x['id'] == star['id'], stars)[0]
                if not existing:
                    stars.append(star)
                else:
                    old = existing['data']
                    new = star['data']
                    start_time = min([x['time'] for x in new])
                    for i in range(len(old)):
                        # Delete overlap if exists
                        if old[i]['time'] >= start_time:
                            old = old[:i]
                            break
                    existing['data'] = old + new
    return stars

def load_neutron_stars(run_dir, run_name):
    """Given a run directory address, loads the run data into mongoDB"""
    client = MongoClient()
    db = client.neutron_stars
    collection = db[run_name]
    collection.insert_many(parse_run(os.path.join(run_dir, run_name)))

def main():
    params = {
        'star_num': [10, 20, 40, 80, 160],
        'rad': [26],
        'metallicity': ['02', '002']
    }
    dir_name = 'N{0}K_r{1}_Z{2}_1'.format(
        params['star_num'][1],
        params['rad'][0],
        params['metallicity'][0]
    )

    data_dir = '/projects/b1011/ageller/NBODY6ppGPU/Nbody6ppGPU-newSE/run/RgSun_NZgrid_BHFLAG2'

    load_neutron_stars(data_dir, dir_name)

if __name__== "__main__":
    main()
