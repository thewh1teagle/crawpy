# crawpy


## Requirements
mongodb database

python3

python3-pip

python3-venv


# How to install 

## Clone the repo 
```git clone 
git clone https://github.com/thewh1teagle/crawpy.git
```

## Create virtual enviroment
```shell
python3 -m venv venv
. venv/bin/activate
```
## Install libaries using pip
```pip
pip install -r requirements.txt
```
## Start the app
```
python3 app.py
```

# How to use

open your browser, and start a scan by navigate into 
```url
http://localhost:8000/scan/?domain=<domain>&max_depth=<max-depth(default=2)>&workers=<num of workers(default=5)>
```
