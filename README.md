# Parser for yarcheplus

This project is parser for site https://yarcheplus.ru/ (2022). 

## Getting Started
Python version: 3.9.10

Chrome version: 98.0.4758.80

Clone project:
```
git clone https://github.com/pymaster13/parser_yarche.git && cd parser_yarche
```

Create and activate virtual environment:
```
python3 -m venv venv && source venv/bin/activate
```

Install libraries:
```
python3 -m pip install -r requirements.txt
```

Run parser for getting categories:
```
python3 get_categories.py
```

Run parser for getting information about products:
```
python3 run.py
```


Configuration features: 
- categories - JSON (keys - tt_id, values - list of categories links).

Example:
```
"categories": {
        "Москва, Вересаева 10": ["/catalog/rastitelnye-masla-130", "/category/moloko-syr-yaytso-175", "/category/moloko-syr-yaytso-176"],
        "Томск, проспект Мира, 20": ["/catalog/rastitelnye-masla-130", "/category/moloko-syr-yaytso-175", "/category/moloko-syr-yaytso-176"]
    }
```

