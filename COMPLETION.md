# Shell Completion for Rencom CLI

> The CLI now supports onboarding (`rencom setup`) and advanced local setup (`rencom fork`). Completion works for all commands.

The Rencom CLI supports shell completion for bash, zsh, fish, and PowerShell.

## Installation

### Bash

To install bash completion:

```bash
# Show the completion script
rencom completion show bash

# Install completion to your bash config
rencom completion install bash --install
```

### Zsh

To install zsh completion:

```bash
# Show the completion script
rencom completion show zsh

# Install completion to your zsh config
rencom completion install zsh --install
```

### Fish

To install fish completion:

```bash
# Show the completion script
rencom completion show fish

# Install completion to your fish config
rencom completion install fish --install
```

### PowerShell

To install PowerShell completion:

```powershell
# Show the completion script
rencom completion show powershell

# Install completion to your PowerShell profile
rencom completion install powershell --install
```

## Manual Installation

If you prefer to install completion manually, you can copy the output of the `show` command to your shell's configuration file:

### Bash
Add to `~/.bashrc` or `~/.bash_profile`

### Zsh
Add to `~/.zshrc`

### Fish
Save to `~/.config/fish/completions/rencom.fish`

### PowerShell
Add to your PowerShell profile (run `$PROFILE` to see the path)

## Uninstalling

To remove completion scripts:

```bash
rencom completion uninstall
```

This will remove completion scripts from all detected shell configuration files.

## Usage

Once installed, you can use tab completion with the `rencom` command:

```bash
rencom <TAB>          # Shows available commands
rencom health <TAB>   # Shows options for health command
rencom token <TAB>    # Shows token subcommands
```

## Troubleshooting

If completion isn't working:

1. Make sure you've restarted your shell or run `source ~/.bashrc` (or equivalent)
2. Verify the completion script was added to your shell config file
3. Check that the `rencom` command is in your PATH
4. For bash, ensure you have bash-completion installed

## Supported Shells

- **Bash**: Requires bash-completion package
- **Zsh**: Built-in completion support
- **Fish**: Built-in completion support  
- **PowerShell**: Windows PowerShell and PowerShell Core