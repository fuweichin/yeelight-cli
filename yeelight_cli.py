#!/usr/bin/env python3
import os
import sys
import json
import inspect
import configparser
from importlib.metadata import version, PackageNotFoundError
from yeelight import discover_bulbs, Bulb

HOME = os.path.expanduser("~").replace("\\", "/")
CONFIG_PATH = HOME + "/.config/yeelight/config.ini"
COMMAND = "yeelight" # or "python yeelight_cli.py" if not installed

def show_version():
    v = ""
    try:
        v = version("yeelight-cli")
    except PackageNotFoundError:
        v = "0.0.0-local"
    print(f"yeelight-cli v{v}")

def show_usage():
    print(f"""Usage:
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
""")

def clean_path(path):
    """Replaces the absolute home directory path with a clean '~' string."""
    if path.startswith(HOME):
        return path.replace(HOME, "~", 1)
    return path

def load_defaults(target_name=None):
    """Loads a specific named device section from the configuration file, with fallbacks."""
    defaults = {
        'ip': None, 'port': 55443, 'effect': 'smooth', 'duration': 300, 'model': None
    }
    
    if not os.path.exists(CONFIG_PATH):
        return defaults, target_name or 'default'

    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)

    # Determine active name configuration if not explicitly passed
    if not target_name:
        if 'default' in config and 'name' in config['default']:
            target_name = config['default']['name']
        else:
            target_name = 'default'

    # Read selected named bulb parameters
    if target_name in config:
        sec = config[target_name]
        if 'ip' in sec: 
            defaults['ip'] = sec['ip']
        if 'port' in sec: 
            defaults['port'] = int(sec['port']) if sec['port'].isdigit() else 55443
        if 'effect' in sec: 
            defaults['effect'] = sec['effect']
        if 'duration' in sec: 
            defaults['duration'] = int(sec['duration']) if sec['duration'].isdigit() else 300
        if 'model' in sec: 
            defaults['model'] = None if sec['model'].lower() in ('none', '') else sec['model']
            
    return defaults, target_name

def save_config(target_name, options):
    """Saves or merges options into a designated named configuration section."""
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_PATH):
        config.read(CONFIG_PATH)
        
    if target_name not in config:
        config[target_name] = {}
        
    for key, value in options.items():
        config[target_name][key] = str(value)
        
    with open(CONFIG_PATH, 'w') as configfile:
        config.write(configfile)
    print(f"Configuration safely merged into [{target_name}] section inside {clean_path(CONFIG_PATH)}")

def parse_args(args):
    """Parses arguments strictly using --name=value format."""
    positionals = []
    kwargs = {}
    for arg in args:
        if arg.startswith('--'):
            opt = arg[2:]
            if '=' in opt:
                key, value = opt.split('=', 1)
                if value.isdigit():
                    value = int(value)
                elif value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
                kwargs[key] = value
            else:
                print("Invalid argument format. Use --key=value.")
                sys.exit(1)
        elif arg.startswith('-'):
            pass
        else:
            positionals.append(arg)
    return positionals, kwargs

def main():
    args = sys.argv[1:]
    if not args:
        show_usage()
        sys.exit(0)

    positionals, kwargs = parse_args(args)

    if not positionals:
        if '--help' in args or '-h' in args:
            show_usage()
            sys.exit(0)
        if '--version' in args or '-v' in args:
            show_version()
            sys.exit(0)
        print("Error: invalid usage. show usage with --help")
        sys.exit(1)

    # Usage 1: Scan bulbs on network via SSDP
    if positionals[0] == 'scan':
        print("Scanning local network for YeeLight devices...")
        bulbs = discover_bulbs()
        print(json.dumps(bulbs, indent=2) if bulbs else "No bulbs found.")
        sys.exit(0)

    # Extract target device name variable early
    target_name = kwargs.pop('name', None)

    if positionals[0] == 'config':
        # Usage 2: read and print the current configuration
        if not kwargs and not target_name:
            if os.path.exists(CONFIG_PATH):
                print(f"Current setup configurations inside {CONFIG_PATH}:")
                config = configparser.ConfigParser()
                config.read(CONFIG_PATH)
                for section in config.sections():
                    print(f"[{section}]")
                    for key, value in config[section].items():
                        print(f"  --{key}={value}")
            else:
                print(f"No configuration file found at {CONFIG_PATH}")
            sys.exit(0)

        # Usage 3: write the provided configuration options to the ini file
        valid_keys = {'ip', 'port', 'effect', 'duration', 'model', 'name'}
        filtered_config = {k: v for k, v in kwargs.items() if k in valid_keys}
        
        # If they only passed --name with no other kwargs, they might want to set the global default pointer
        if target_name and not filtered_config:
            save_config('default', {'name': target_name})
            sys.exit(0)

        if not filtered_config and not target_name:
            print("Error: No valid configuration options provided.")
            sys.exit(1)
            
        # Target the specific device section or fall back to default
        section_name = target_name or 'default'
        save_config(section_name, filtered_config)
        sys.exit(0)

    # Usage 4: Execute Bulb Action
    defaults, active_name = load_defaults(target_name)
    ip = kwargs.pop('ip', defaults['ip'])
    port = kwargs.pop('port', defaults['port'])
    effect = kwargs.pop('effect', defaults['effect'])
    duration = kwargs.pop('duration', defaults['duration'])
    model = kwargs.pop('model', defaults['model'])

    if not ip:
        print(f"Error: No IP found for device/section '{active_name}'. Supply via '--ip=<address>' or run config setup.")
        sys.exit(1)

    method_name = positionals[0]
    
    try:
        bulb = Bulb(ip, port=port, effect=effect, duration=duration, model=model)
        
        if not hasattr(bulb, method_name):
            print(f"Error: Method '{method_name}' does not exist.")
            sys.exit(1)
            
        method = getattr(bulb, method_name)
        
        if not inspect.ismethod(method):
            print(f"Current state/property value: {method}")
            sys.exit(0)

        result = method(**kwargs)
        if result is not None:
            print(json.dumps(result, indent=2) if isinstance(result, (dict, list)) else result)
        else:
            print("Success.")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
