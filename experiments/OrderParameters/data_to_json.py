#!/usr/bin/env python3
"""
Converting OP dat file into properly organized JSON format.

Notes:
- Amount of each molecule in the membrane is given as a ratio.
- For a membrane of single molecule it's 1.
"""

import re
import sys
import json
import math
from collections import Counter
from fairmd.lipids.auxiliary.jsonEncoders import CompactJSONEncoder


def read_input_data(path_to_data):
    # define input dic
    data = {}

    # set standard parameter
    DEFAULT_OP_ERROR = 0.02
    PLACEHOLDER_AMB_CODE = ""
    PLACEHOLDER_NEF_ATOM = ""

    # read the file
    with open(path_to_data) as OPfile:
        lines = OPfile.readlines()
        for line in lines:
            # run check and decide, if line is considered
            line = re.sub(r"#.*$", "", line).strip()
            if line == "":
                continue
            lSplit = line.split()
            #print(lSplit)
            assert len(lSplit) in [3, 4, 5, 6]
            if math.isnan(float(lSplit[2])):
                continue
            # extract parameters line by line
            OPname = lSplit[0] + " " + lSplit[1]
            err = DEFAULT_OP_ERROR if len(lSplit)<=3 or math.isnan(float(lSplit[3])) else float(lSplit[3])
            amb = PLACEHOLDER_AMB_CODE if len(lSplit)<=4 or math.isnan(int(lSplit[4])) else int(lSplit[4])
            nef = PLACEHOLDER_NEF_ATOM if len(lSplit)<=5 or lSplit[5] in ["NaN","nan"] else str(lSplit[5])
            OPvalues = [float(lSplit[2]), err]
            Ambiguities = [amb,nef]
            # add data to dic
            data[str(OPname)] = [OPvalues,Ambiguities]

    return(data)


def get_default_ambiguityCodes_NEFAtomName(data):
    # INFO:
    # the ambiguity code was introduced by BMRB to express the reliability
    #	of assignments.
    # for more info see: https://bmrb.io/deposit/shifts_example_help.shtml
    # SUMMARY:
    #	The values other than 1 are used for those atoms with different
    #	chemical shifts that cannot be assigned to stereospecific atoms
    #	or to specific residues or chains.
    #
    #	Index	Definition
    #	1	Unique (including isolated methyl protons, geminal atoms, and
    #		geminal methyl groups with identical chemical shifts)
    #		(e.g. ILE HD11, HD12, HD13 protons)
    #	2	Ambiguity of geminal atoms or geminal methyl proton groups
    #		(e.g. ASP HB2 and HB3 protons, LEU CD1 and CD2 carbons, or
    #		LEU HD11, HD12, HD13 and HD21, HD22, HD23 methyl protons)
    #	3	Aromatic atoms on opposite sides of symmetrical rings
    #		(e.g. TYR HE1 and HE2 protons)
    #	4	Intraresidue ambiguities (e.g. LYS HG and HD protons or
    #		TRP HZ2 and HZ3 protons)
    #	5	Interresidue ambiguities (LYS 12 vs. LYS 27)
    #	6	Intermolecular ambiguities (e.g. ASP 31 CA in monomer 1 and
    #		ASP 31 CA in monomer 2 of an asymmetrical homodimer, duplex
    #		DNA assignments, or other assignments that may apply to atoms
    #		in one or more molecule in the molecular assembly)
    #	9	Ambiguous, specific ambiguity not defined

    # PREPARATIONS
    # define dic to convert counts (of H-bonds) to ambiguity code
    dicCounts2Code = {1:1, 2:2, 3:2}

    # ASSIGN AMBIGUITY CODES AND NEF ATOM NAME
    # extract all C atoms and unique
    AtomCarbUniqueCounts = Counter(key.split()[0] for key in data.keys())

	# in the file, each column represents a specififc C-H bond, so,
    # the number of occurances (n) of a C-atom corresponds to the number
    #	of attached H-atoms:
    #		n=1	group=CH	ambiguity code=1	NEF atom=H1
    #		n=2	group=CH2	ambiguity code=2	OP(H1)!=OP(H2)	NEF atom=Hx and Hy
    #		n=2	group=CH2	ambiguity code=2	OP(H1)==OP(H2)	NEF atom=H%
    #		n=3	group=CH3	ambiguity code=2	NEF atom=H%
    # so, lets iterate over the rows and determine the ambiguity code
    for key, value in data.items():
        # get the counts (number of connected H-atoms) for the corresponding
        #	C-atom of teh current row
        AtomCarbon = key.split()[0]
        AtomHydrogen = key.split()[1]
        counts = AtomCarbUniqueCounts[AtomCarbon]

        # ASSIGN DEFAULT BMEB AMBIGUITY CODE
        # check, if the BMRB code is not assigned: value is ""
        # data[key][1][0] is the "address" for the BMRB code
        if data[key][1][0] == "":
            # based on the counts (number of H-atoms), assign the default
            #	ambiguity codes (can be adjusted later, if needed)
            data[key][1][0] = dicCounts2Code[counts]

        # ASSIGN DEFAULT NEF ATOM NAME
        # check, if the NEF atom name is not assigned: value is ""
        # data[key][1][1] is the "address" for the NEF atom name
        if data[key][1][1] == "":
            # based on the counts (number of H-atoms), assign the default
            #	ambiguity codes (info above)
            if counts == 1:
                # CH group - this is clearly H
                data[key][1][1] = "H1"
            elif counts == 2:
                # CH2 group
                # check, if OP(Hx)==OP(Hy):
                #	first, extract both values
                #   item[0][0] is the OP value
                OP_Hx, OP_Hy = [item[0][0] for key, item in data.items() if key.split()[0] == AtomCarbon]
                if OP_Hx == OP_Hy:
                    # if both values are the same, add the "H%"
                    data[key][1][1] = "H%"
                else:
                    #  we need to assign x and y to the name (1->x,2->y)
                    if "H1_" in AtomHydrogen:
                        data[key][1][1] = "Hx"
                    elif "H2_" in AtomHydrogen:
                        data[key][1][1] = "Hy"
                    else:
                        # this case should not be reached - however, if this is
                        #	the case, simply add NaN
                        data[key][1][1] = "NaN"
            elif counts == 3:
                # CH3 group - this is magnetically equivalent, so add "H%"
                data[key][1][1] = "H%"
            else:
                # this case should not be reached - however, if this is
                #	the case, simply add NaN
                data[key][1][1] = "NaN"

    return(data)



def main(data_file):
    # PRINT INFORMATION TO SCREEN
    print("Converting from: ", data_file)
    outfile = data_file.replace(".dat", ".json")
    print("Converting to:\t ", outfile)
    # standard parameters are defined in the function read_input_data

    # READ THE INPUT DATA
    data = read_input_data(data_file)

    # ADD DEFAULT BMRB CODE AND NEF ATOM NAME
    # if needed, add the standard BMRB ambiguity coe and NEF atom name
    # unknown NEF AND BMRB  fields to fill are currently ""
    data = get_default_ambiguityCodes_NEFAtomName(data)

    # WRITE OUT THE FINAL JSON FILE
    with open(outfile, "w") as f:
        json.dump(data, f, cls=CompactJSONEncoder)


if __name__ == "__main__":
    if len(sys.argv)==2:
        main(sys.argv[1])
    else:
        raise ValueError(
            "  AN ERROR OCCURED:\n    Usage: data_to_json.py <data_file>\n"
            )
