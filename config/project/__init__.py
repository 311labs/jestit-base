import os
import importlib
from jestit.helpers import paths, modules
from imp import load_module


# configure from the current folder and go 1 folder back
paths.configure_paths(__file__, 1)
# build djangos INSTALLED_APPS
paths.configure_apps()
print("="*80)
import traceback
# traceback.print_stack()
import sys
# print(sys.path)
for app in paths.INSTALLED_APPS:
    print(app)
print("="*80)

# Set default profile
VAR_PROFILE = "local"
# Check if a profile file exists and override VAR_PROFILE
VAR_PROFILE_FILE = os.path.join(paths.VAR_ROOT, "profile")
if os.path.exists(VAR_PROFILE_FILE):
    with open(VAR_PROFILE_FILE, "r") as f:
        VAR_PROFILE = f.read().strip()

# load the paths into globals
modules.load_module_to_globals(paths, globals())

# Dynamically import the local defaults
module = modules.load_module("project.defaults", __name__)  # now lets the local defaults override it
# load all the variables into global memory
modules.load_module_to_globals(module, globals())
print(DEBUG)
# Dynamically import the correct profile module
# module = modules.load_module(f"project.{VAR_PROFILE}", __name__)  # now lets the profile override it
# globals().update(vars(module))
