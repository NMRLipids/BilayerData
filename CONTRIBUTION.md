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

## Database self-maintainance

BilayerData is an on-GitHub database and it has a set of workflows to perfom
its own maintanance.

**Self-checks** are run every time a contributor adds a commit to pull request.
Please do not ignore them. Their output can guide you how to improve your
metadata or point to errors.

**Simulation ID uniqueness** is maintained by auto-PRs. Each simulation is
added with negative ID and then it adds PR to fix it. It ensures uniqueness of
IDs.

**Quality recomputations** are also performed with auto-PRs. If one is
contributing to experiments or simulations, it's not required to run matching
or quality evaluation - it will be run by our self-maintanence system automatically.
However, if your changes breaks further analysis, it's good to know about it, so we
recommend to run quality evaluation to check that it works.

_Security notes:_ AutoPRs cannot be triggered by an external contributors because they
are triggered by merging. Merging a PR, in turn, requires the approve of organisation member,
so auto-PRs cannot be triggered silently.

## Versioning policy and releases

BilayerData is a developing database. It has a lot of various manifest files that can
change their schemas at some point. We have semantic version `vX.Y.Z` system where `X` is
a major version, `Y` is called minor version, and `Z` is a patch. We increase:

- the patch `Z` when we decide that contirbution to the database is significant since previous patch
- minor version `Y` when some schemas were changed
- major version `X` when the project reaches the next large milestone

Versions are released so we can cite the release of the database from external documents that is
simpler than cite commit hashes.


