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
                break
            try:
                stars.append({
                    'id': int(data_line[0]),
                    'type': int(data_line[1]),
                    'mass': float(data_line[2]),
                    'luminosity': float(data_line[3]),
                    'radius': float(data_line[4]),
                    'spin': float(data_line[12])
                })
            # In case the sev file is incorrectly formatted
            except ValueError:
                print "Incorrectly formatted sev file detected. Ignoring incorrecty formatted data from:"
                print sev_name

    print 'parsed ' + sev_name

    return { "time": physical_time, "stars": stars }

def parse_bev(bev_name):
    """Takes in a bev file address and returns the physical time and a list of stars

    output format: {
        'time': float,
        'stars': [
            {
                'id': int,
                'type': int,
                'binary_id': int
            }, ...
        ]
    }
    """

    stars = []
    with open(bev_name, 'r') as f:
        row = f.readline().split()

        # Physical time is the second item in the first line
        physical_time = float(row[1])

        for line in f:
            data_line = line.split()
            if int(data_line[0]) == -1000: # -1000 is the sentinel value indicating EOF
                break
            # For the first star:
            stars.append({ 'id': int(data_line[0]), 'type': int(data_line[2]), 'binary_id': int(data_line[1]) })
            # For the second star:
            stars.append({ 'id': int(data_line[1]), 'type': int(data_line[3]), 'binary_id': int(data_line[0]) })

    print 'parsed ' + bev_name

    return { "time": physical_time, "stars": stars }

def get_escapes(save_dir):
    """Takes in a save directory and  outputs a list of dictionaries with the
        following keys: id, time, type; where id is the star id, time is the
        star's escape time, and type is the star type.
    """

    escapes = []
    with open(os.path.join(save_dir, "esc.11"), 'r') as f:
        try:
            # Skip the header
            next(f)
        except StopIteration: # Empty file
            return []
        
        for line in f:
            data_line = line.split()
            escapes.append({
                "id": int(data_line[5]), # id is the 6th item in row
                "time": float(data_line[0]), # Physical time is 1st item in row
                "type": int(data_line[4]) # Star type is the 5th item in row
            })

    print 'parsed escapes from ' + save_dir

    return escapes

def parse_save(save_dir):
    """Takes in a save directory address and returns a list of stars.

    Data should be sorted by 'time'.

    output format: [
        {
            'id': int,
            'data': [
                {
                    'time': float,
                    'type': int,
                    'binary': bool,
                    'binary_id': int or None
                }, ...
            ],
            'escape': float or None
        }, ...
    ]
    """

    files = os.path.join(save_dir, 'sev.83_*')

    stars = []
    for filename in glob.glob(files): # For each sev file:
        sev_data = parse_sev(filename)
        for star in sev_data['stars']:
            matching_star = filter(lambda x: x['id'] == star['id'], stars)
            if matching_star: # If this star has already been found and initialized
                matching_star[0]['data'].append({
                    'time': sev_data['time'],
                    'type': star['type'],
                    'binary': False,
                    'binary_id': None
                })
            else: # If not, initialize star
                stars.append({
                    'id': star['id'],
                    'data': [{
                        'time': sev_data['time'],
                        'type': star['type'],
                        'binary': False,
                        'binary_id': None
                    }],
                    'escape': None
                })

    files = os.path.join(save_dir, 'bev.82_*')

    for filename in glob.glob(files): # For each bev file:
        bev_data = parse_bev(filename)
        for star in bev_data['stars']:
            matching_star = filter(lambda x: x['id'] == star['id'], stars)
            if matching_star:
                matching_star[0]['data'].append({
                    'time': bev_data['time'],
                    'type': star['type'],
                    'binary': True,
                    'binary_id': star['binary_id']
                })
            else:
                stars.append({
                    'id': star['id'],
                    'data': [{
                        'time': bev_data['time'],
                        'type': star['type'],
                        'binary': True,
                        'binary_id': star['binary_id']
                    }],
                    'escape': None
                })

    # Select only neutron stars
    neutron_stars = []
    for star in stars:
        found = False
        for timepoint in star['data']:
            if timepoint['type'] == NEUTRON_STAR:
                found = True
                break
        if found:
            neutron_stars.append(star)

    # Get escape data
    escape = get_escapes(save_dir)
    for star in escape:
        found = next((item for item in neutron_stars if item['id'] == star['id']), None)
        if found:
            found['escape'] = star['time']

    # Sort
    for star in neutron_stars:
        star['data'] = sorted(star['data'], key=lambda x: x['time'])

    print 'save dir parsed: ' + save_dir

    return neutron_stars

def parse_run(run_dir):
    """Given a run directory address, returns a list of stars

    output format: [
        {
            'id': int,
            'data': [
                {
                    'time': float,
                    'type': int,
                    'binary': bool,
                    'binary_id': int or None
                }, ...
            ],
            'escape': float or None
        }, ...
    ]
    """
    files = os.path.join(run_dir, 'save0*')

    stars = []
    for save_dir in glob.glob(files):
        data = parse_save(save_dir)
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

    print 'run parsed ' + run_dir

    return stars

def load_neutron_stars(run_dir, run_name):
    """Given a run directory address, loads the run data into mongoDB"""
    client = MongoClient()
    db = client.neutron_stars
    collection = db[run_name]
    collection.insert_many(parse_run(os.path.join(run_dir, run_name)))

def main():
    params = {
        'star_num': [10, 20, 40],
        'rad': [26],
        'metallicity': ['02', '002']
    }
    dir_name = 'N{0}K_r{1}_Z{2}_1'.format(
        params['star_num'][0],
        params['rad'][0],
        params['metallicity'][0]
    )

    data_dir = '/projects/b1011/ageller/NBODY6ppGPU/Nbody6ppGPU-newSE/run/RgSun_NZgrid_BHFLAG2'

    load_neutron_stars(data_dir, dir_name)

if __name__== "__main__":
    main()
