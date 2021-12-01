# LV-Client

# Requirements
1. **gradle** Only version 6.x supported!
~~~
$ brew install gradle@6
~~~

2. **Java Version 1.8**

### Build(Optional)
~~~
$ gradle build
$ cp build/libs/LV-Client.jar ./
~~~

## Test Client Run
~~~
$ java -jar LV-Client.jar -m 0
~~~

## Command line Run
### Make Clues
~~~
$ java -jar LV-Client.jar -t "my secret" -n 3 -th 2
$ cat clues.txt
$ mv clues.txt clues
~~~

## Test tool
Written in python, the tool helps you to test LiteVault System.
It provides below features:
- Get storage info: create authorization to Manager (BACKUP_REQUEST & ISSUE_VID_REQUEST)
- Get storage token: create authorization to Storages (TOKEN_REQUEST)
- Manage clues: store and restore clues (STORE_REQUEST & CLUE_REQUEST)

### Install the tool
`$ pip install -e .[dev]`

> need python 3.7.3 or above

### Before started
- Prepare clues by using [java cli tool](### Command line Run)
- Run Manager and Storages

### Getting started
- `$ lv-tool -h`

OR run testing shell

[local]
```
./run.sh [clue_file_path]  # GetStorages -> TOKEN -> STORE -> READ
./run.sh                   # GetStorages -> TOKEN -> READ
```
[testbed]
```
./run_testbed.sh [clue_file_path] 
```

### Restore Clues
~~~
$ java -jar LV-Client.jar -f restored_clues.txt -e 0
$ cat decrypt.txt
~~~

## QA
Using the 'locust' library for integration testing and automated QA.

[local]
```
$ locust -f locust_files/full_scenario_local.py
```
[testbed]
```
$ locust -f locust_files/full_scenario_testbed.py
```

Connect to http://localhost:8089/ and test.
