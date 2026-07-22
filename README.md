# yeelight-cli
A dynamic, full-featured CLI wrapper around the [python-yeelight](https://yeelight.readthedocs.io/en/latest/index.html) package.

## Installation
```sh
# install remote release
pip install yeelight-cli

# install local copy
cd yeelight-cli
pip install -e .
```

## Usage

```txt
Usage:
1. Discover YeeLight bulbs over LAN.
  yeelight scan
2: Register a bulb in ~/yeelight/config.ini
  yeelight config [OPTIONS]
3: Set default bulb
  yeelight config --name=NAME
4. Call bulb method of python-yeelight
  yeelight [OPTIONS] <METHOD> [PARAMS]
5. Print help message
  yeelight [MISC]

MISC:
    --help,-h        print usage
    --version,-v     print version
OPTIONS:
    --name           monitor-light
    --ip             192.168.1.5
    --port           55443
    --effect         smooth
    --duration       300
    --model          None

METHOD:
    turn_off         (light_type=0)
    turn_on          (light_type=0)
    cron_add         (event_type=0,value) minutes for event_type=0, seconds for event_type=1
    cron_del         (event_type=0)
    cron_get         (event_type=0)
    get_capabilities (timeout=2) timeout is in seconds
    set_name         (name)
    set_brightness   (brightness, light_type=0)
    set_default      (light_type=0)
    set_power_mode   (mode)
    set_scene        (scene_class,light_type=0)
    set_color_temp   (degrees, light_type=0)
    set_rgb          (red, green, blue, light_type=0)
    set_hsv          (hue, saturation, value, light_type=0)
    ...and more

PARAMS:
    --light_type     0
    --brightness     80
    ...and more

For bulb methods and parameters, see
https://yeelight.readthedocs.io/en/latest/yeelight.html
```

## Frequent-used Features

```sh
# discover bulbs over LAN via a SSDP-like protocol
yeelight scan
# get bulb info
yeelight --ip=192.168.1.5 get_capabilities

# rename a bulb
yeelight --ip=192.168.1.5 set_name --name=monitor-light
# Note: "default" is reserved and cannot be used as name
# register a bulb
yeelight config --name=monitor-light --ip=192.168.1.5 --model=lamp15 --effect=smooth --duration=400
# set default bulb (for later use when calling method without --ip or --name)
yeelight config --name=monitor-light

# rename another bulb
yeelight --ip=192.168.1.6 set_name --name=beside-light
# register another bulb
yeelight config --name=beside-light --ip=192.168.1.6 --model=lamp9 --effect=smooth --duration=400

# inspect bulb registerations (~/yeelight/config.ini)
yeelight config

# turn on bulb
yeelight turn_on            # by default name (if registered and made default)
yeelight --ip=192.168.1.6 turn_on       # by ip
yeelight --name=monitor-light turn_on   # by name (if registered)

# turn on ambient light (for specific models, e.g. lamp15)
yeelight turn_on --light_type=1

# set brightness (1~100) with explicit transition
yeelight set_brightness --brightness=50 --effect=smooth --duration=1000

# set color temperature (2700~6500)
yeelight set_color_temp --degresss=6500

# turn off bulb
yeelight turn_off
yeelight turn_off --light_type=1

```

## Build

```sh
# install build tools
pip install --upgrade build twine
# run build
python -m build
# test locally without publishing
pip install dist/yeelight_cli-0.1.0-py3-none-any.whl
```

## Publish to Test PyPI

```sh
pip uninstall yeelight-cli

# Create a production account on Test PyPI
# generate a production API token Account Settings > API Tokens
python -m twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ yeelight-cli
```

## Publish to PyPI

```sh
pip uninstall yeelight-cli

# Create a production account on PyPI
# generate a production API token Account Settings > API Tokens
python -m twine upload dist/*
pip install --index-url https://pypi.org --extra-index-url https://pypi.org yeelight-cli
```

