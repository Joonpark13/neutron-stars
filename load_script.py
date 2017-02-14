import os

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

def parse_save(save_dir):
    """Takes in a save directory address and returns a list of stars.

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
    pass

def main():
    params = {
        'star_num': [10, 20, 40, 80, 160],
        'rad': [26],
        'metallicity': ['02', '002']
    }

    data_dir = os.path.join(
        'data',
        # "N{0}K_r{1}_Z{2}_*".format(
        'N{0}K_r{1}_Z{2}_1'.format(
            params['star_num'][0],
            params['rad'][0],
            params['metallicity'][0]
        )
    )

    sev = os.path.join(data_dir, 'save01', 'sev.83_0.000')
    print parse_sev(sev)

if __name__== "__main__":
    main()
