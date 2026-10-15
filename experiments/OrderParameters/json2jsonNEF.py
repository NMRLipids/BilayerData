#!/usr/bin/python3
'''
Converts old json files and adds the BMRB ambiguity code and the NEF atom naming

for detailed information see comments in function:
	get_ambiguityCodes_NEFAtomName

10.09.2026
added during FAIRMD workshop at LINX in Lund by Tobi R

INPUT:
	- PathJsonFile (string):
		the path to the old json file to be converted
OUTPUT:
	- converted json file with included ambiguity code and NEF atom naming
	- format of json entry:
		"<AtomNameCarbon> <AtomNameHydrogen>": [
			[<OrderParameter>, <OrderParameterError>(optional)],
			[<BMRB ambiguity code>, <NEF atom name>]
		]
OPTIONS:
	- addMissingError (bool):
		if no <OrderParameterError> is given in the INPUT json, it is possible
		to add an <DEFAULT_OP_ERROR> (see main function) by setting
		addMissingError = True

TO DO:
	- add option for adding partially missing errors
'''

import sys
import json
import pandas as pd
from fairmd.lipids.auxiliary.jsonEncoders import CompactJSONEncoder

def read_json_files(PathData):
	# read in the jason data
	with open(PathData) as f:
		data = json.load(f)
	# however, later we need a pandas dataframe which has the C and the H-Atoms
	#	in seperate colums --> this is important for getting the NEF names
	# first, get a list for teh new rows
	rows = []
	# then split the key in both atoms and get the first value list as seperated
	#	columns in the new rows
	for key, value in data.items():
		# gets C and H atom
		atomC, atomH = key.split()
		# get OP value and its error (if available)
		if len(value[0])==1:
			# CASE: only OP available and no error
			OP = value[0][0]
			rows.append([atomC, atomH, OP])
		elif len(value[0])==2:
			# CASE: OP and its error are available
			OP, OP_error = value[0]
			rows.append([atomC, atomH, OP, OP_error])
		else:
			# another option is not possible, so raise exception
			raise ValueError( f"Expected 1 (only Order parameter) or 2 (Order paraemter and its error) elements, but got {len(value)}: {value}" )
	# make dataframe by adding all rows
	tabData = pd.DataFrame(rows)
	if len(rows[0])==3:
		# if error is not available, only name the three exsiting columns
		tabData.columns = ["AtomCarbon", "AtomHydrogen", "OP"]
	else:
		# if error is available, add the name
		tabData.columns = ["AtomCarbon", "AtomHydrogen", "OP","OP_error"]
	# return
	return(tabData)


def get_ambiguityCodes_NEFAtomName(tabData):
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
	AtomCarbUniqueCounts = tabData["AtomCarbon"].value_counts()
	# in the file, each column represents a specififc C-H bond, so,
	# the number of occurances (n) of a C-atom corresponds to the number
	#	of attached H-atoms:
	#		n=1	group=CH	ambiguity code=1	--- NEF atom=H1
	#		n=2	group=CH2	ambiguity code=2	OP(H1)!=OP(H2)	NEF atom=Hx and Hy
	#		n=2	group=CH2	ambiguity code=2	OP(H1)==OP(H2)	NEF atom=H%
	#		n=3	group=CH3	ambiguity code=2	--- 	NEF atom=H%
	# initialize list for values
	listAmbiguityCodes=[]
	listNEFAtomNames=[]
	# so, lets iterate over the rows and determine the ambiguity code
	for IDX, ROW in tabData.iterrows():
		# get the counts (number of connected H-atoms) for the corresponding
		#	C-atom of teh current row
		counts = AtomCarbUniqueCounts[ROW["AtomCarbon"]]
		# based on the counts (number of H-atoms), assign the ambiguity codes
		#	codes of 2 can be changed later
		listAmbiguityCodes.append(dicCounts2Code[counts])
		# assign the NEF atom name - more complex
		if counts == 1:
			# CH group - this is clearly H
			listNEFAtomNames.append("H1")
		elif counts == 2:
			# CH2 group
			# check, if OP(Hx)==OP(Hy):
			#	first, extract both values
			OP_Hx, OP_Hy = tabData.loc[tabData["AtomCarbon"] == ROW["AtomCarbon"], "OP"]
			if OP_Hx == OP_Hy:
				# if both values are the same, add the "H%"
				listNEFAtomNames.append("H%")
			else:
				#  we need to assign x and y to the name (1->x,2->y)
				if "H1_" in ROW["AtomHydrogen"]:
					listNEFAtomNames.append("Hx")
				elif "H2_" in ROW["AtomHydrogen"]:
					listNEFAtomNames.append("Hy")
				else:
					# this case should not be reached - however, if this is
					#	the case, simply add nothing
					listNEFAtomNames.append("")
		elif counts == 3:
			# CH3 group - this is magnetically equivalent, so add "H%"
			listNEFAtomNames.append("H%")
		else:
			# this case should not be reached - however, if this is
			#	the case, simply add nothing
			listNEFAtomNames.append("")

	return(listAmbiguityCodes,listNEFAtomNames)


def add_missing_OP_error(tabData,DEFAULT_OP_ERROR):
	# check first, if errors exist
	if "OP_error" in tabData.columns:
		# stop script and raise python error message,
		#	if OP error is submitted already with the input
		raise ValueError("Order Parameter Errors are already provided; default errors cannot be added. Set <addMissingError> to <False>.")

	# otherwise create list with default errors
	listDefaultErrs = [DEFAULT_OP_ERROR]*tabData.shape[0]
	# and add the default OP errors
	tabData["OP_error"] = listDefaultErrs

	# return
	return(tabData)


def rewrite_json_file(PathDatFile,tabData):
	# first get the path of the new file
	PathDatFileNew = PathDatFile[:-5]+"_NEF.json"

	# create empty dic to write out data as .json
	data = {}

	# iterate over tabData and write out the rows in the dic
	for _, row in tabData.iterrows():
		# get the identifier by combining C and H atom names
		identifier = f"{row['AtomCarbon']} {row['AtomHydrogen']}"
		# if the error is submitted, add the error, otherwise not
		if "OP_error" in tabData.columns:
			data[identifier] = [ [row["OP"],row["OP_error"]], [row["AmbiguityCode"],row["AtomNEF"]] ]
		else:
			data[identifier] = [ [row["OP"]], [row["AmbiguityCode"],row["AtomNEF"]] ]

	# write the JSON file
	# the remaining code is only there to get a more matching style
	with open(PathDatFileNew, "w") as f:
		json.dump(data, f, cls=CompactJSONEncoder)


def main(PathJsonFile,addMissingErrors=False):
	# READ JSON FILE
	# get the .json files data
	PathJsonFile = PathJsonFile
	tabData = read_json_files(PathJsonFile)

	# IF SWITCHED ON, ADD DEFAULT ERRORS
	# if errors for order paraemeters are missing, add default error, if the
	#	corresponding option is activated:
	DEFAULT_OP_ERROR = 0.02
	# check, if error should be added:
	if addMissingErrors:
		tabData = add_missing_OP_error(tabData,DEFAULT_OP_ERROR)

	# AMBIGUITY CODE AND NEF ATOM NAMES
	# get the ambiguity codes and add the NEF atom name; for explannations
	#	see the corresponding function
	listAmbiguityCodes,listNEFAtomNames = get_ambiguityCodes_NEFAtomName(tabData)
	# add both lists as columns to the tabData
	tabData["AmbiguityCode"] = listAmbiguityCodes
	tabData["AtomNEF"] = listNEFAtomNames

	# WRITE NEW JSON OUTPUT
	# write out new json files in fairmd "CompactJSONEncoder" format
	rewrite_json_file(PathJsonFile,tabData)


if __name__ == "__main__":
	if len(sys.argv)==2:
		main(sys.argv[1])
	elif len(sys.argv) == 3 and sys.argv[2] in ("True", "False"):
		main(sys.argv[1], sys.argv[2] == "True")
	else:
		raise ValueError(
			"Usage: json2jsonNEF.py <PathToOldJson: str> [<addMissingErrors: bool>]\n"
			)

#main("json_files/test3.json")
