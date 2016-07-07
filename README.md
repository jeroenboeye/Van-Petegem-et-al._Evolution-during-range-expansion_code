# Van-Petegem-et-al._Evolution-during-range-expansion_code
Added simulation files

This repository contains the files for the simulation in the research paper "Spatial selection and local adaptation jointly shape life-history evolution during range expansion" published in the American Naturalist by Van Petegem et al. (2016).

---------------------------------------------------------------------------------------------------------------------------------

There are 4 shell scripts.
--------------------------

man_shell1.sh and main_shell_ng1.sh contain loops over parameter values that are passed on to the sub_shell scripts. 
The 'ng' in the second file stands for 'no gradient', same goes for the other files in this repository.


sub_shell.sh and sub_shell_ng.sh receive parameter values from the main shell scripts mentioned above.
These scripts have three functions:
  -Set parameters for a job on the UGent High Performance Computer (how long the simulation will take etc.)
  -Receive parameter values from the main scripts and pass them on to the individual python scripts.
  -Initiate the actual job with the settings metioned above.
  
There are 2 python scripts.
-----------------------------
mite_model.py contains the code for a scenario with an environmental gradient.
mite_model_ng.py contains the code for a scenario without an environmental gradient.
These scripts are activated with the sub_shell scripts mentioned above and return a text file with the results when finished.
