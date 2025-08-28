# Adding simulations and experiments

Adding new data is described in detail in [the NMRlipids documentation](https://nmrlipids.github.io/). Please follow the instructions carefully for both simulations and experiments, filling metadata fields with meaningful and complete information.

# Adding molecules
If data addition requires a molecule that is currently absent, you are very welcome to add new molecules. Please be careful with modifying molecule information, especially mapping files of molecules, as it could affect the recomputation of other contributors' data.

To add a new molecule please add a mapping file as described in [https://nmrlipids.github.io/moleculesAndMapping.html#universal-atom-names-in-mapping-files](https://nmrlipids.github.io/moleculesAndMapping.html#universal-atom-names-in-mapping-files)

Please provide metadata about the molecule in a `metadata.yaml` in the same subfolder of `Molecules/membrane/YOURMOLECULE`. You can find the template in `Molecules/metadata-example.yaml`
The recommended workflow is to start from the [InChI](https://en.wikipedia.org/wiki/International_Chemical_Identifier). You can obtain the InChI and InChIKey for your molecule via different methods. One possiblity is to use a PDB snapshot of your trajectory (from gromacs, VMD, MDAnalysis ...) and to add connectivty using [RDkit](https://www.rdkit.org/) or [gromologist](https://gitlab.com/KomBioMol/gromologist) and convert a single molecule to InChI via [RDkit](https://www.rdkit.org/) or [OpenBabel](https://openbabel.org/index.html). We use the neutral form of the molecule. Please indicate the charge of the molecule in your `metadata.yaml` under `charge:`.
Please ensure that the InChI represents your molecule. The named tools might deliver imperfect results.
Provided your molecule is not fully synthetic or novel, you can obtain most of the other metadata from the [PubChem API](https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest) and the [UniChem API](https://www.ebi.ac.uk/unichem/api/docs) using the InChIKey.
Mapping especially to LIPID MAPS and SwissLipids might be incomplete in some cases and can be completed manually. 


# Repository rules

1. You can add new data without referring to any issues.
1. Please keep main branch in your fork updated so that it can be rebased (we prefer rebasing over merging).
2. Once you address an issue, please refer it in commit message by using phrases like 'Partially fixes #000'.
3. We recommend contributors to squash commits if the changes are just adding new data.
4. We require at least one review from organisation member to accept a pull-request.
5. Check representation of yourself in `AUTHORS.md` file.
6. You are always welcome to participate in repository discussions and NMRlipids community events to develop data and code together.

