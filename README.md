# PyFS
Midnight Commander Python-based VFS module

## Usage
 * Link or copy main file to ~/.local/share/mc/extfs.d/pyfs.py

 * Add this code block to ~/.config/mc/mc.ext:
```bash
# pyfs
shell/i/.pyfs
        Open=%cd %p/pyfs.py://
        View=%view{ascii} cat %f
```

 * Can also be used manually:
```bash
cd test.pyfs/pyfs://
```
