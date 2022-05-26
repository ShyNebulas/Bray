# Bray
A simple and minimal habit tracker for Todoist.

### Prerequisites

The things you need before installing the software.

- Python 3.10.4 or greater

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 

Start with cloning the repository:

```git clone https://github.com/ShyNebulas/Bray.git```

An enviromental file must be made which will contain your Todoist API key.

```
cd Bray
echo TODOIST_API_TOKEN = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX > .env
```

Next, in ``.config/config.yaml`` your project ID (for the project where you want to store your habits) should be added. 

You can find your project ID by using the web version of Todoist, where the numbers at the end of your URL is the ID.

```
https://todoist.com/app/project/XXXXXXXXXX
```

Now we need to install the Python dependencies:

```
cd src
python3 -m venv ./venv
source venv/bin/activate
pip3 install -r ../requirements.txt
```

## Usage

To run Bray simple type:

```
python3 main.py
```

It's recommended that you run Bray every midnight, or there about,  as it will check if you have completed your habits and increment or reset them based on that.

Each task should be in the format:

```
Task name [Day 0]
```

With each task having a due date or time.