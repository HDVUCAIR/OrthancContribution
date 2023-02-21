# Purpose
Create a constellation of [Orthanc servers](https://www.orthanc-server.com) and accompanying PostGreSQL servers for purposes of DICOM anonymization, distribution and organization on disk.  The servers are built upon the [Osimis docker image](https://hub.docker.com/r/osimis/orthanc), modified to extend scripting capability.  See README.build for instructions.

A lookup table is maintained in the PostGreSQL server in order to support the anonymization of longitudinal studies for the same patient.  In full anonymization mode, each patient has their visits shifted by a random number of days (one random setting per patient, same setting for each study).  

The anonymization was created to maintain reference links between series within a study.  This is handled by recursively examining existing links between all DICOM and reproducing those links with anonymized UID.

# Status
I built a lot of this setup in the days when Lua was the only [embedded scripting language](https://book.orthanc-server.com/users/lua.html) available to the Orthanc.  This setup is currently in flux as I convert my old Lua scripts to use the more powerful [Python plugin](https://book.orthanc-server.com/plugins/python.html?highlight=python) capability.  Eventually, I plan to replace all the Lua scripts with Python.

# Current Issues
- The anonymizing Orthanc can be run with or without OnStableStudy detection (whether in the original Lua or newer Pyton scripts).  I sometimes see ongoing anonymizations fail when interrupted by the OnStableStudy of another recently uploaded study.  I suspect this has to do with job collisions on the back end.  I hope to address this with better job management in the future.  For the moment, if I plan on running multiple anonymizations, I turn off the OnStableStudy feature.
- The output DICOM are currently not completely DICOM compliant, based on [Dave Clunie's DICOM validator](https://www.dclunie.com/dicom3tools/dciodvfy.html).  This is mainly a problem of deleting one or two DICOM key/value pairs that are required, but can be set to blank values.

# Goals
- Fix the job (collision?) problems with better use of [Orthanc's job management](https://book.orthanc-server.com/users/advanced-rest.html?highlight=jobs#jobs)
- Repair non-DICOM compliance of output
- Revisit and re-validate HIPAA compliance of output anonymized DICOM
