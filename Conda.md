# Creating Conda packages for cloudmesh

* Step 1 - Download anaconda latest version by running command - 
  
  ```
  mkdir condavm
  cd condavm
  vagrant init generic/ubuntu1810
  vagrant up
  vagarnt ssh
  
  sudo apt-get update
  # wget https://repo.anaconda.com/archive/Anaconda3-2018.12-Linux-x86_64.sh

  # curl -O https://repo.continuum.io/archive/Anaconda3-5.0.1-Linux-x86_64.sh
  #sh Anaconda3-2018.12-Linux-x86_64.sh -b
  
  wget https://repo.continuum.io/archive/Anaconda3-5.0.1-Linux-x86_64.sh
  
  # sh Anaconda3-5.0.1-Linux-x86_64.sh -b
  
  sudo sh Anaconda3-2018.12-Linux-x86_64.sh -b -u -p /usr/local
  
  export PATH="/usr/local/anaconda3/bin:$PATH"
  ```

* Step 4 - run  - 

  ```
  conda config --set anaconda_upload yes
  ```
  
* Step 5 - Clone the 
* Step 6 - conda build cloudmesh.common (This will build and upload cloudmesh.common)
* Step 7 - When prompted, Enter credentials to the anaconda.org
* Step 8 - Run - conda build cloudmesh.sys (This will build and upload cloudmesh.sys)
* Step 9 - Run - conda build cloudmesh.cmd5 (This will build and upload cloudmesh.cmd5)
* Step 10 - Run - conda build cloudmesh.openapi (This will build and upload cloudmesh.openapi)
* Step 11 - All packages are now uploaded to the anaconda.org
