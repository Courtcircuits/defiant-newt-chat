# Documentation

## MkDocs

An HTML version of the μD3TN documentation is created via [MkDocs](https://www.mkdocs.org/). All files stored in the MkDocs directory are taken into account. The MkDocs configuration can be changed in the `mkdocs.yaml` file. To add further pages to the navigation, they must be added to the `nav` section.

### Prepare

```sh
# w/o nix
pip install -U mkdocs
pip install $(mkdocs get-deps)

# w/ nix
nix develop '.?submodules=1'
```

### Develop

```sh
mkdocs serve
```

### Build

```sh
# w/o nix
mkdocs build --strict --site-dir result/

# w/ nix
nix build .#mkdocs-html
```

### Deploy

When changes are made to the master branch, the latest version of the documentation is automatically built and published at https://d3tn.gitlab.io/ud3tn.

## Man Page

There exists also a man page for μD3TN, which can be viewed with

```sh
man --local-file ud3tn.1
```
