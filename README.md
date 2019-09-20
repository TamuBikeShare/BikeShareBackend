# CSCE 482: Bike Sharing

This semester we're working with Texas A&M's Transportation Department in order to generate a solution to the existing bike share problem on campus. In specific we're looking at creating a heatmap of both the where rides begin as well as where they end. Furthermore we hope to be able to perform some predictive analysis on the datasets in order to better know when to rebalance bicycles. Finally if time permits, we hope to be able to plan routes for the transportation department to aide them in their rebalancing.

## Getting Started

These next sections will be filled in with info as we begin the project.

### Prerequisites


### Installing

Install pyenv

```https://github.com/pyenv/pyenv#installation```

Install python version 3.7.4

```pyenv install 3.7.4```

Install your distro's postgresql (or configure config.py for the location of your postgres server)

```sudo apt-get install postgresql postgresql-contrib```

Install your distro's equivalent of [libpq-dev](https://packages.debian.org/sid/libpq-dev)

```sudo apt-get install libpq-dev```

Initialize your python environment

```python3.7 -m venv env```

Source your env

```source env/bin/activate```

Install requirements

```pip install -r requirements.txt```

Initialize the config file and edit it for your settings

```cp config.py.example config.py```

```vim config.py```

Uncomment the create db line from app.py and run app.py

```python app.py```

Begin scraping data

```python scrape.py```

## Running the tests


### Break down into end to end tests


### And coding style tests


## Deployment


## Built With

* [AngularJS](https://angularjs.org/) - Our web framework
* [Node.js](https://nodejs.org/en/) - Backend technology
* [Python](https://www.python.org/) - Used to perform machine learning on the data

## Contributing

## Versioning

Please follow the [SemVer](http://semver.org/) guidelines for versioning.

## Authors

* **Jacob Ericson** - *Initial work* - [jacobericson](https://github.tamu.edu/jacobericson/)
* **Isaac Decastro** - *Initial work* - [isaacfdec](https://github.tamu.edu/isaacfdec/)
* **Ryan Bilek** - *Initial work* - [a152252](https://github.tamu.edu/a152252/)
* **Cole Boggus** - *Initial work* - [cboggus](https://github.tamu.edu/cboggus/)
* **Amir Karimloo** - *Initial work* - [newbeg89](https://github.tamu.edu/newbeg89/)


## License


## Acknowledgments

* Texas A&M Transportation
* Dr. Goldberg and Edgar Hernandez
* Dr. Hammond and Josh Cherian
