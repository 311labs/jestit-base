#!/usr/bin/env python
import os
import sys
from django.core.management import execute_from_command_line
import paths

def main():
    paths.load_apps()
    # paths.load_settings()
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project')
    try:
        execute_from_command_line(sys.argv)
    except Exception as exc:
        raise RuntimeError("Management command execution failed") from exc

if __name__ == '__main__':
    main()
