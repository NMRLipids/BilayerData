# Contribution guidelines

Please read the corresponding parts of the document before you start contributing.

## Contributing the database: simulations, experiments, and molecules

_Adding_ new data is described in detail in [the FAIRMD Lipids
documentation](https://databank.readthedocs.io/stable/dbcontribute.html).
Please follow the instructions carefully for both simulations and experiments,
filling metadata fields with meaningful and complete information.

When you find mistakes in the data, please inform the community by opening [an
issue](https://github.com/NMRLipids/BilayerData/issues/new?template=bug_data.yml)
or open a pull-request if you want to fix it by yourself.

_Deleting_ data is possible and very welcome _iff_ you can approve that the
data is problematic. It is applicable first of all for the experiments because
incorrect experiments affects the quality. Incorrect simulations will just get
very bad quality, however if there is a mistaken simulation, duplicated
trajectory or fraud, it can also be deleted.

**Labels** 

Please use one of our dedicated labels for opening issues or marking your PR:

- `contribution:mol`
- `contribution:exp`
- `contribution:sim`
- `bug:data` if a mistake was found

## Repository rules

1. Anyone can contribute. For contribution, we don't force one to create an
   issue first.

2. We require at least one review from organisation member to accept a
   pull-request.

3. Please keep main branch in your fork updated so that it can be rebased (we
   prefer rebasing over merging).

4. Once you address an issue, please refer it in commit message by using
   phrases like 'Partially fixes #000'.

5. We recommend contributors to squash commits if there is no use in storing history.

5. Check representation of yourself in `AUTHORS.md` and `CITATION.cff` files.

6. Everyone is always welcome to participate in repository discussions and
   NMRlipids community events to develop data and code together.


