#!/usr/bin/python3
'''
Converts old dat files and adds the BMRB ambiguity code and the NEF atom naming

for detailed information see comments in function:
	get_ambiguityCodes_NEFAtomName

10.09.2026
added during FAIRMD workshop at LINX in Lund by Tobi R

INPUT:
	- PathDatFile (string):
		the path to the old dat file to be converted
OUTPUT:
	- converted dat file with included ambiguity code and NEF atom naming
	- columns of the output are:
		<AtomNameCarbon>
		<AtomNameHydrogen>
		<OrderParameter>
		<OrderParameterError
		<BMRB ambiguity code>
		<NEF atom name>
'''


import re
import sys
import pandas as pd

def read_dat_files(PathData):
	# read datas as pandas data frame
	tabData = pd.read_table(PathData,sep=r"\s+",comment="#",header=None)
	# check, if the dataframe has 3 (no OP error) or 4 (with OP error) columns
	if tabData.shape[1]==3:
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
			# do the check, but also check, if one of the values is NaN, if so,
			#	do not assign H%, but use Hx and Hy
			if OP_Hx == OP_Hy and ~pd.isna(OP_Hx) and ~pd.isna(OP_Hy):
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


def rewrite_dat_file(PathDatFile,tabData):
	# first get the path of the new file
	PathDatFileNew = PathDatFile[:-4]+"_NEF.dat"

	# first open new output file
	with open(PathDatFileNew,"w") as FilDatNew:
		# then open the old file:
		# we want to keep all previous comments from the olf file in the new one
		with open(PathDatFile,"r") as FilDatOld:
			# iterate over lines
			for line in FilDatOld:
				# check the type of teh line
				if line[0] == "#":
					# if the old line is a comment (starting with "#")
					#	just add it to the new file
					FilDatNew.write(line)
				elif line =="\n":
					# if the old line is an empty line
					#	just add it to the new file
					FilDatNew.write(line)
				else:
					# otherwise add the data
					parts = re.split(r"\s+", line)
					newLine = tabData.loc[(tabData["AtomCarbon"]==parts[0]) & (tabData["AtomHydrogen"]==parts[1])].iloc[0]
					# change "nan" to the previous "NaN" format
					newLine = newLine.where(pd.notna(newLine), "NaN")
					#write out the line
					FilDatNew.write(" ".join(map(str, newLine)) + "\n")


def main(PathDatFile):
	# READ JSON FILE
	# get the .dat files data
	PathDatFile = PathDatFile
	tabData = read_dat_files(PathDatFile)

	# AMBIGUITY CODE AND NEF ATOM NAMES
	# get the ambiguity codes and add the NEF atom name; for explannations
	#	see the corresponding function
	listAmbiguityCodes,listNEFAtomNames = get_ambiguityCodes_NEFAtomName(tabData)
	# add both lists as columns to the tabData
	tabData["AmbiguityCode"] = listAmbiguityCodes
	tabData["AtomNEF"] = listNEFAtomNames

	# WRITE NEW .DAT OUTPUT
	rewrite_dat_file(PathDatFile,tabData)


if __name__ == "__main__":
	if len(sys.argv)==2:
		main(sys.argv[1])
	else:
		raise ValueError(
			"Usage: dat2datNEF.py <PathToOldDat: str>\n"
			)

#main("dat_files/test.dat")
