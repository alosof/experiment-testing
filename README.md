# Introduction to automated testing

## Setup

```bash
conda create -n experiment-testing python=3.10.6
conda activate experiment-testing
pip install -r requirements.txt
python -m ipykernel install --user --name=experiment-testing
```

## Run "production" instrument server

```bash
make instrument
```

## Run test instrument server

```bash
make instrument_test
```

## Run all tests

```bash
make tests
```
