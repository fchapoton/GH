# Graph Homolgy

Compute the cohomology dimensions of graph complexes.

## Getting Started

### Prerequisites
This graph homology library is based on the sage math library. Install the [sage math](http://www.sagemath.org) library and activate the sage shell:
```
$ sage -sh
```
Install the pandas and tqdm modules:
```
(sage-sh)$ pip -install tqdm
(sage-sh)$ pip -install pandas
```
Furthermore, in order to generate graphs up to isomorphism the graph library [nauty](http://pallini.di.uniroma1.it/) is needed.

Small matrices can be handled using the sage function to compute exact ranks.

In order to determine ranks of large matrices [linbox](https://github.com/linbox-team) and or [rheinfall](https://github.com/riccardomurri/rheinfall)
are required. 
For rank computations the corresponding example code of [linbox](https://github.com/linbox-team/linbox/blob/master/examples/rank.C) or 
[rheinfall](https://github.com/riccardomurri/rheinfall/blob/master/src.c%2B%2B/examples/rank.cpp) is used.
Replace the rank files by the ones provided in [this](https://github.com/sibrun/GH/tree/master/linbox_rheinfall_rank) folder and compile them.
Finally, move the executables to the folder [GH/linbox_rheinfall_rank](https://github.com/sibrun/GH/tree/master/linbox_rheinfall_rank).

### Docker
The easiest way to install the prerequisists and use the library is to run it in a Docker container.

Change to the folder [GH/docker](https://github.com/sibrun/GH/tree/master/docker) and build the Docker image from the Dockerfile:
```
$ docker build -t <name docker image> .
```
Alternatively pull an existing docker image with the current state of the GH library from 
[Docker Hub](https://hub.docker.com/repository/docker/sibrun/ubuntu-gh):
```
$ docker pull sibrun/ubuntu-gh:<tagname>
```
In order to detach the shell later from the process and keep the process running in the background activate a tmux shell:
```
$ tmux
```
Continue inside the tmux shell.
Mount a persistent storage location to the Docker container and run the docker image. 
The generated data will be stored in the persistent storage location:
```
$ docker run -it -v <path to persistant storage location>:/root/GH/gh_data <name docker image:tagname> /bin/bash
```
For developing purposes mount the [GH/source](https://github.com/sibrun/GH/tree/master/source) 
folder of a copy of the GH library to the Docker container, such that the Docker container keeps track of changes in the source code:
```
$ docker run -it -v <path to GH library>/GH/source:/root/GH/source <name docker image:tagname> /bin/bash
```
It is possible to mount both the source directory as well as the data directory to the Docker container:
```
$ docker run -it -v <path to GH library>/GH/source:/root/GH/source -v <path to persistant storage location>:/root/GH/gh_data <name docker image:tagname> /bin/bash
```
Run a command from the GH library (as stated below) inside the Docker container:
```
$ sage --python ... 
```
In order to detach the process from the tmux shell first press `ctrl+b` release and after that press `d`.

## Running the tests

Change to the [GH](https://github.com/sibrun/GH) directuory to run the tests:
```
$ sage --python ./source/TestOrdinaryGraphComplex.py
$ sage --python ./source/TestOrdinaryGraphBiComplex.py
$ sage --python ./source/TestHairyGraphComplex.py
$ sage --python ./source/TestHairyGraphBiComplex.py
$ sage --python ./source/TestBiColoredHairyGraphComplex.py
$ sage --python ./source/TestBiColoredHairyGraphBiComplex.py
```

## Running the examples

The file [GraphHomology.py](https://github.com/sibrun/GH/blob/master/source/GraphHomology.py) provides commands to run the implemented
examples. 

Change to the directory GH and build the basis for the ordinary graph complex with odd edges:
```
$ sage --python ./source/GraphHomology.py ordinary -op1 contract -v 3,12 -l 0,9 -odd_e -n_jobs 4 -build_b
```
Afterwards build the operator matrices of the conctract edges and delete edges differentials: 
```
$ sage --python ./source/GraphHomology.py ordinary -op1 contract -v 3,12 -l 0,9 -odd_e -n_jobs 4 -build_op
$ sage --python ./source/GraphHomology.py ordinary -op1 delete -v 3,12 -l 0,9 -odd_e -n_jobs 4 -build_op
```
Then compute the ranks of the operator matrices:
```
$ sage --python ./source/GraphHomology.py ordinary -op1 contract -v 3,12 -l 0,9 -odd_e -n_jobs 4 -sage mod -rank
$ sage --python ./source/GraphHomology.py ordinary -op1 delete -v 3,12 -l 0,9 -odd_e -n_jobs 4 -sage mod -rank
```
Finally test whether the operators square to zero, i.e. build a differential, whether they anti-commute and plot the 
cohomology dimensions of the associated graph complexs for each differential:
```
$ sage --python ./source/GraphHomology.py ordinary -op1 contract -op2 delete -v 0,12 -l 0,9 -odd_e -square_zero -anti_commute -cohomology
```
The comhomology dimensions of the bicomplex with the two differentials contract edges and delete edges can be computed with:
```
$ sage --python ./source/GraphHomology.py ordinary -bicomplex contract_delete -d 0,18 -odd_e -n_jobs 4 -sage mod -build_b -build_op -rank -square_zero -cohomology -csv
```

More examples for hairy graph complexes can be found in the file [GraphHomology.py](https://github.com/sibrun/GH/blob/master/source/GraphHomology.py).

Feel free to extend this library with more examples of graph complexes.

## Documentation
In order to generate a documentation using [sphinx](http://www.sphinx-doc.org/en/master/#) change to the folder 
[GH/docs](https://github.com/sibrun/GH/tree/master/docs) activate the sage shell and generate a html documentation with:
```
(sage-sh)$ make html
```
The html documentation will be found under GH/docs/build/html/idex.html.

## Authors

* **Simon Brun** 
* **Thomas Willwacher**

## License


## Acknowledgments



