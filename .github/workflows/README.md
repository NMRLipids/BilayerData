# Information on workflows related to processing simulation files

There are currently two workflows operating on data from users linked to the related web interface:

`ProcessInfoFile.yml` and `RunGlobalAnalysis.yml`

**ProcessInfoFile.yml:**  will run scripts: addData and calcProperties which computes data related to the newly added simulation. These scripts are located in the Databank repository.

**RunGlobalAnalysis.yml:**  will run scripts: searchDatabank,  QualityEvaluation, and makeRanking.

The separation here is to avoid merge conflicts if multiple users add new simulations prior to them getting merged.

Some more information about the workflows:

## ProcessInfoFile.yml
**Purpose:**  Processing of the user-data info.yml

**Uses environment:** `user_data_addition` which requires specific reviewers to approve the workflow run. This is a level of protection against malicious use of the web interface. This environment can be changed from settings in this repository:

Settings -> Environments -> user_data_addition

**User-data-fork:** This workflow makes changes to a user-data fork, currently: `MagnusSletten/BilayerData`. Changing the fork will include changing references to it inside this workflow and in `RunGlobalAnalysis.yml`. Changing the "if" keys is sufficient here for both workflows.

**NREC-Usage:**  This workflow also runs using NREC resources due to the limitation in memory of default github runners. 

## RunGlobalAnalysis.yml

This workflow does not require heavy computation and the default github runner is sufficient. 

It runs when simulation files are merged into main specifically from the user data repository. 



