# hugo-outliner

Create an outline from JSON file.

`hugo-outliner` will call `hugo new` command recursively according to the input JSON file.

## Requirements

```sh
pip3 install -r requirements.txt
```

## Usage

```sh
cd path-to-hugo-project-root  # there should be a config.toml file in the directory
python3 hugo-outliner.py outline-sample.json
```

## Outline JSON format

```json
{
  "Chapters": [
    {
      "Title": "String",
      "Name": "String",
      "Weight": "Integer",
      "Sections": [
        {
          "Title": "String",
          "Name": "String",
          "Weight": "Integer"
        }
      ]
    }
  ]
}
```

- `Title` [required]: Any String, which will be the title of this page (chapter or section).
- `Name` [required]: String that match `^[a-zA-Z0-9_]+$` (alphabet, number, and underscore), which will be the directory name of this page (chapter or section).
- `Weight` [optional]: Any integer, the chapters and sections will be sorted ascent order of the weight, if not specfied, the order will the determined by the writtern order (top to bottom).
