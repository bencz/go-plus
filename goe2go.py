#!/usr/bin/env python3
"""
Main CLI for Go-Extended
Supports single files and complete projects
"""

import sys
import argparse
from pathlib import Path
from project_manager import ProjectManager
from main import main as transpile_single_file

def cmd_init(args):
    """Initialize a new project"""
    project_root = Path(args.directory) if args.directory else Path.cwd()
    manager = ProjectManager(project_root)
    
    go_mod = args.module if args.module else f"github.com/user/{args.name}"
    manager.init_project(args.name, go_mod)

def cmd_build(args):
    """Build the project"""
    project_root = Path(args.directory) if args.directory else Path.cwd()
    manager = ProjectManager(project_root)
    
    try:
        manager.transpile_project()
    except Exception as e:
        print(f"Error during build: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

def cmd_info(args):
    """Show project information"""
    project_root = Path(args.directory) if args.directory else Path.cwd()
    manager = ProjectManager(project_root)
    
    try:
        manager.show_project_info()
    except Exception as e:
        print(f"Error getting project information: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()

def cmd_transpile(args):
    """Transpile a single file"""
    # Reuse existing functionality
    sys.argv = ['main.py', args.input]
    if args.output:
        sys.argv.extend(['-o', args.output])
    if args.verbose:
        sys.argv.append('-v')
    
    transpile_single_file()

def cmd_run(args):
    """Build and run the project"""
    import subprocess
    
    # First build
    cmd_build(args)
    
    # Then run
    project_root = Path(args.directory) if args.directory else Path.cwd()
    manager = ProjectManager(project_root)
    config = manager.load_config()
    
    build_dir = project_root / config.output_dir
    main_file = None
    
    # Search for main file
    for go_file in build_dir.rglob("*.go"):
        with open(go_file, 'r') as f:
            content = f.read()
            if 'package main' in content and 'func main()' in content:
                main_file = go_file
                break
    
    if not main_file:
        print("Main file not found")
        sys.exit(1)
    
    print(f"Running {main_file.relative_to(project_root)}...")
    try:
        result = subprocess.run(['go', 'run', main_file.name], 
                              cwd=main_file.parent, 
                              check=True)
    except subprocess.CalledProcessError as e:
        print(f"Execution error: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description='Go-Extended Transpiler - Classes and exceptions support for Go',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initialize new project
  goe2go init myproject --module github.com/user/myproject
  
  # Build project
  goe2go build
  
  # Build and run
  goe2go run
  
  # Transpile single file
  goe2go transpile input.gox -o output.go
  
  # Show project information
  goe2go info
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize new project')
    init_parser.add_argument('name', help='Project name')
    init_parser.add_argument('--module', help='Go module name (go.mod)')
    init_parser.set_defaults(func=cmd_init)
    
    # Build command
    build_parser = subparsers.add_parser('build', help='Build the project')
    build_parser.add_argument('-d', '--directory', help='Project directory')
    build_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode')
    build_parser.set_defaults(func=cmd_build)
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Build and run the project')
    run_parser.add_argument('-d', '--directory', help='Project directory')
    run_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode')
    run_parser.set_defaults(func=cmd_run)
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show project information')
    info_parser.add_argument('-d', '--directory', help='Project directory')
    info_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode')
    info_parser.set_defaults(func=cmd_info)
    
    # Transpile command (single file)
    transpile_parser = subparsers.add_parser('transpile', help='Transpile single file')
    transpile_parser.add_argument('input', help='Input Go-Extended file')
    transpile_parser.add_argument('-o', '--output', help='Output Go file')
    transpile_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode')
    transpile_parser.set_defaults(func=cmd_transpile)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    args.func(args)

if __name__ == '__main__':
    main()
