# transform dat files to json
# TODO: use a propper JSON formatter

import json
import sys

def _round_value(x: str | float | int) -> float:
    """
    Converts the value to float and round it to 4 decimal places.
    """
    return round(float(x), 4)


data_file = sys.argv[1]
print(data_file)
if '.dat' in data_file:
    outfile = data_file.replace(".dat", "_FormFactor.json")
if '.xff' in data_file:
    outfile = data_file.replace(".xff", "_FormFactor.json")
print(outfile)

data = []

with open(data_file) as OPfile:
    lines = OPfile.readlines()
    for line in lines:
        if "#" in line or line == "\n":
            continue
        print(line.split())
        if len(line.split()) == 3:
            values = [_round_value(line.split()[0]),
                      _round_value(line.split()[1]),
                      _round_value(line.split()[2])]  # , float(line.split()[3])]
        # SAMULI: If error is not given in the original file, error of 0.02 is assumed.
        if len(line.split()) == 2:
            # , float(line.split()[3])]
            values = [_round_value(line.split()[0]),
                      _round_value(line.split()[1]),
                      0.02]

        data.append(values)

with open(outfile, 'w') as f:
    json.dump(data, f)
