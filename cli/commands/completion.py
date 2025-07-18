#!/usr/bin/env python3
"""
Shell completion support for Rencom CLI
"""

import click
import os
import sys
from pathlib import Path


@click.group(name='completion')
def completion():
    """Shell completion commands"""
    pass


@completion.command()
@click.argument('shell', type=click.Choice(['bash', 'zsh', 'fish', 'powershell']))
@click.option('--install', is_flag=True, help='Install completion script to shell config')
def install(shell: str, install: bool):
    """Generate and optionally install shell completion scripts"""
    
    # Get the completion script
    completion_script = get_completion_script(shell)
    
    if not completion_script:
        click.echo(f"Completion not supported for {shell}", err=True)
        return
    
    if install:
        install_completion_script(shell, completion_script)
    else:
        click.echo(completion_script)


@completion.command()
@click.argument('shell', type=click.Choice(['bash', 'zsh', 'fish', 'powershell']))
def show(shell: str):
    """Show completion script for the specified shell"""
    completion_script = get_completion_script(shell)
    
    if not completion_script:
        click.echo(f"Completion not supported for {shell}", err=True)
        return
    
    click.echo(completion_script)


def get_completion_script(shell: str) -> str:
    """Generate completion script for the specified shell"""
    
    if shell == 'bash':
        return get_bash_completion()
    elif shell == 'zsh':
        return get_zsh_completion()
    elif shell == 'fish':
        return get_fish_completion()
    elif shell == 'powershell':
        return get_powershell_completion()
    
    return ""


def get_bash_completion() -> str:
    """Generate bash completion script"""
    return '''# Rencom CLI bash completion
_rencom_completion() {
    local IFS=$'\\n'
    local response

    response=$(env COMP_WORDS="${COMP_WORDS[*]}" COMP_CWORD=$COMP_CWORD _RENCOM_COMPLETE=bash_complete $1)

    for completion in $response; do
        IFS=',' read type value <<< "$completion"

        if [[ $type == 'dir' ]]; then
            COMPREPLY=()
            compopt -o dirnames
        elif [[ $type == 'file' ]]; then
            COMPREPLY=()
            compopt -o default
        elif [[ $type == 'plain' ]]; then
            COMPREPLY+=($value)
        fi
    done

    return 0
}

complete -o nosort -F _rencom_completion rencom
'''


def get_zsh_completion() -> str:
    """Generate zsh completion script"""
    return '''#compdef rencom

_rencom_completion() {
    local -a completions
    local -a completions_with_descriptions
    local -a response
    (( ! $+commands[rencom] )) && return 1

    response=("${(@f)$(env COMP_WORDS="${words[*]}" COMP_CWORD=$((CURRENT-1)) _RENCOM_COMPLETE=zsh_complete rencom)}")

    for type_and_completion in "${response[@]}"; do
        completions_with_descriptions+=("$type_and_completion")
        completions+=("${type_and_completion%%:*}")
    done

    if [ "$completions" ]; then
        _describe '' completions_with_descriptions -V unsorted
    fi
}

compdef _rencom_completion rencom
'''


def get_fish_completion() -> str:
    """Generate fish completion script"""
    return '''# Rencom CLI fish completion
complete -c rencom -f -a "(env _RENCOM_COMPLETE=fish_complete COMP_WORDS=(commandline -cp) COMP_CWORD=(commandline -t) rencom)"
'''


def get_powershell_completion() -> str:
    """Generate PowerShell completion script"""
    return '''# Rencom CLI PowerShell completion
Register-ArgumentCompleter -Native -CommandName rencom -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)
    
    $env:_RENCOM_COMPLETE = "powershell_complete"
    $env:COMP_WORDS = $commandAst.ToString()
    $env:COMP_CWORD = $commandAst.CommandElements.Count - 1
    
    rencom 2>&1 | ForEach-Object {
        [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
    }
    
    Remove-Item Env:_RENCOM_COMPLETE
    Remove-Item Env:COMP_WORDS  
    Remove-Item Env:COMP_CWORD
}
'''


def install_completion_script(shell: str, script: str):
    """Install completion script to appropriate shell config file"""
    
    home = Path.home()
    
    if shell == 'bash':
        # Try common bash config files
        config_files = [
            home / '.bashrc',
            home / '.bash_profile',
            home / '.profile'
        ]
        
        for config_file in config_files:
            if config_file.exists():
                install_to_file(config_file, script, shell)
                return
        
        # If no config file exists, create .bashrc
        install_to_file(home / '.bashrc', script, shell)
        
    elif shell == 'zsh':
        # Try common zsh config files
        config_files = [
            home / '.zshrc',
            home / '.zsh_profile'
        ]
        
        for config_file in config_files:
            if config_file.exists():
                install_to_file(config_file, script, shell)
                return
        
        # If no config file exists, create .zshrc
        install_to_file(home / '.zshrc', script, shell)
        
    elif shell == 'fish':
        # Fish completions go in a specific directory
        fish_dir = home / '.config' / 'fish' / 'completions'
        fish_dir.mkdir(parents=True, exist_ok=True)
        
        completion_file = fish_dir / 'rencom.fish'
        completion_file.write_text(script)
        
        click.echo(f"Completion script installed to {completion_file}")
        
    elif shell == 'powershell':
        # PowerShell profile
        try:
            import subprocess
            result = subprocess.run(['powershell', '-Command', '$PROFILE'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                profile_path = Path(result.stdout.strip())
                profile_path.parent.mkdir(parents=True, exist_ok=True)
                install_to_file(profile_path, script, shell)
            else:
                click.echo("Could not determine PowerShell profile location", err=True)
        except Exception as e:
            click.echo(f"Error installing PowerShell completion: {e}", err=True)


def install_to_file(config_file: Path, script: str, shell: str):
    """Install completion script to a specific config file"""
    
    marker_start = f"# BEGIN RENCOM CLI COMPLETION ({shell})"
    marker_end = f"# END RENCOM CLI COMPLETION ({shell})"
    
    # Read existing content
    if config_file.exists():
        content = config_file.read_text()
    else:
        content = ""
    
    # Remove existing completion if present
    lines = content.split('\n')
    new_lines = []
    skip = False
    
    for line in lines:
        if line.strip() == marker_start:
            skip = True
        elif line.strip() == marker_end:
            skip = False
            continue
        elif not skip:
            new_lines.append(line)
    
    # Add new completion
    new_lines.extend([
        "",
        marker_start,
        script.strip(),
        marker_end,
        ""
    ])
    
    # Write back to file
    config_file.write_text('\n'.join(new_lines))
    
    click.echo(f"Completion script installed to {config_file}")
    click.echo(f"Please restart your shell or run: source {config_file}")


@completion.command()
def uninstall():
    """Remove completion scripts from shell config files"""
    
    home = Path.home()
    
    # List of potential config files to check
    config_files = [
        home / '.bashrc',
        home / '.bash_profile', 
        home / '.profile',
        home / '.zshrc',
        home / '.zsh_profile'
    ]
    
    removed_count = 0
    
    for config_file in config_files:
        if config_file.exists():
            if remove_completion_from_file(config_file):
                removed_count += 1
    
    # Remove fish completion
    fish_completion = home / '.config' / 'fish' / 'completions' / 'rencom.fish'
    if fish_completion.exists():
        fish_completion.unlink()
        click.echo(f"Removed fish completion: {fish_completion}")
        removed_count += 1
    
    if removed_count > 0:
        click.echo(f"Removed completion scripts from {removed_count} file(s)")
        click.echo("Please restart your shell for changes to take effect")
    else:
        click.echo("No completion scripts found to remove")


def remove_completion_from_file(config_file: Path) -> bool:
    """Remove completion script from a config file"""
    
    content = config_file.read_text()
    lines = content.split('\n')
    new_lines = []
    skip = False
    found = False
    
    for line in lines:
        if "BEGIN RENCOM CLI COMPLETION" in line:
            skip = True
            found = True
        elif "END RENCOM CLI COMPLETION" in line:
            skip = False
            continue
        elif not skip:
            new_lines.append(line)
    
    if found:
        config_file.write_text('\n'.join(new_lines))
        click.echo(f"Removed completion from {config_file}")
        return True
    
    return False