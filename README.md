# nli Python API

An elegantly simple Encoding and Decoding of Location to eNLI Codes (Natural Location Identifier).

Reference: https://e-nli.org/enli-code

## Install

## Usage
See Postman documentation.

### Start Server Option 1:  Docker Hosted

Docker
```
docker-compose -f docker-compose.yaml build --no-cache && docker-compose -f docker-compose.yaml up

echo detached
docker-compose -f docker-compose.yaml build --no-cache && docker-compose -f docker-compose.yaml up -d
```

### Start Server Option 2:  Machine Hosted
Navigate to the root directory of the repo, and run:
```
python main.py
```

