# hugo-outliner

Create an outline from JSON file.

`hugo-outliner` will call `hugo new` command recursively according to the input JSON file.

## Requirements

```sh
pip3 install -r requirements.txt
```

## Usage

```sh
cd path-to-hugo-project-root  # there should be config.toml file in the directory
python3 hugo-outliner.py outline-sample.json
```
