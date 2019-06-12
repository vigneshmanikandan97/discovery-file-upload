# discovery-file-upload
Python script to operate on Watson Discovery Collections - Upload Documents

## Directions for Use
* Please run from virtual source
  ```
  pip install virtualenv
  ```
  then..
  ```
  virtualenv venv
  ```
  then..
  ```
  venv\Scripts\activate (on Windows)
  source venv (linux)
  ```
* Make sure you have all requirements
  ```
  pip install -r requirements.txt
  ```

## Script Features
This script contains methods to perform CRUD on Watson Discovery Collection.

## Command Line arguments (AI Search workflow)

### Starting the workflow
#### Workflow without training
* To start the entire discovery workflow, run this command.
```
python discovery_helper.py -sw
```

#### Workflow with training
* To start the workflow and also train discovery instance, run this command.
```
python discovery_helper.py -sw -t
```

### Relevancy Training
* To train discovery instance, run this command.
```
python discovery_helper.py -t
```

### Create / Update / Delete - Collection / Configuration
* To create, update or delete a collection or configuration, run this command.
* Note that the kwargs in '[]' are mutually exclusive, i.e. only provide one kwarg.
```
python discovery_helper.py -action=[create, update, delete] [-collection, -config]
```

### Read / List - Collection / Configuration
You can either list all or one collection or configuration
```
python discovery_helper.py -list=[all, one] [-collection, -config]
```
#### Note
If you use ```-list=one```, the program will prompt for collection or configuration ID because it is mandatory.


&copy;Aruba Networks
