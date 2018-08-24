# docs

This folder contains our docs and how to recreate them.

## Recreating docs with `setup.py`


### Creating the modules directory for apidocs

Perform the below command in the root directory of this package. First, remove all of the existing files.

```bash
rm -rf docs//modules/*.rst

sphinx-apidoc HTSeqCountCluster/ -o docs/modules
```
