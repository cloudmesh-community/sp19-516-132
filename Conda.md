# Creating Conda packages for cloudmesh

* Step 1 - Uzip the zip file on your local laptop
* Step 2 - Open conda prompt and run conda install conda-build
* Step 3 - Create an account in anaconda.org
* Step 4 - run  - conda config --set anaconda_upload yes
* Step 5 - Navigate to the unzipped directory
* Step 6 - conda build cloudmesh.common (This will build and upload cloudmesh.common)
* Step 7 - When prompted, Enter credentials to the anaconda.org
* Step 8 - Run - conda build cloudmesh.sys (This will build and upload cloudmesh.sys)
* Step 9 - Run - conda build cloudmesh.cmd5 (This will build and upload cloudmesh.cmd5)
* Step 10 - Run - conda build cloudmesh.openapi (This will build and upload cloudmesh.openapi)
* Step 11 - All packages are now uploaded to the anaconda.org
