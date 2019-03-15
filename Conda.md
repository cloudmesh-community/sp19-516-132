# Creating Conda packages for cloudmesh

BUG install this in non sudo


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
  conda config --set anaconda_upload yes
  conda config --env --add channels conda-forge
  
  export SRC=`pwd`
  git clone https://github.com/cloudmesh/cloudmesh.common.git
  git clone https://github.com/cloudmesh/cloudmesh.cmd5.git
  git clone https://github.com/cloudmesh/cloudmesh.sys.git
  git clone https://github.com/cloudmesh/cloudmesh.openapi.git
  git clone https://github.com/cloudmesh-community/cm.git
  ```
  
* Step 6 - conda build cloudmesh.common (This will build and upload cloudmesh.common)

  ```
  cd $SRC/cm/conda
  conda build cloudmesh.common
  conda build cloudmesh.cmd5
  conda build cloudmesh.sys
  ```
  
* Install the packages

  ```
  sudo conda install -y -c laszewski cloudmesh.cmd5
  sudo conda install -y -c laszewski cloudmesh.sys
  ```
