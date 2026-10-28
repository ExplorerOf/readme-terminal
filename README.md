<h1 align="center">readme-terminal</h1>

<p align="center">
  An animated terminal for your GitHub profile README.<br>
  One Python file, zero dependencies, one SVG that lives in your repo.
</p>

<p align="center">
  <img src="example.svg" width="800" alt="Animated Windows terminal typing whoami and type stack.json" />
</p>

<p align="center">
  <a href="#windows">Windows</a> ·
  <a href="#linux">Linux</a> ·
  <a href="#macos">macOS</a> ·
  <a href="#let-github-do-it-no-python-needed">GitHub Actions</a> ·
  <a href="#config-reference">Config</a> ·
  <a href="#tips-and-troubleshooting">Tips</a>
</p>

## Why

- **Zero dependencies.** Only the Python standard library. Nothing to `pip install`.
- **No external service.** Most typing widgets are loaded from someone else's server. This one is a file in your repo, so it never goes down and never hits a rate limit.
- **Feels like a real terminal.** Commands are typed one by one, output shows up when the command finishes, a cursor blinks at the end, and then it all plays again.
- **Three looks.** Windows Terminal, Linux (GNOME/Ubuntu) and macOS, with colored prompts and any theme you want.
- **Made for GitHub.** Pure SVG animation: no JavaScript, no embedded fonts. It plays inside a plain `<img>` tag.
- **Runs itself.** Optional GitHub Action regenerates the SVG every time you edit the config, so you don't even need Python.

## How it goes

Whatever your system, it is the same four steps:

1. **Get** `terminal_svg.py` and an example config.
2. **Edit** the config: your name, your commands, your colors.
3. **Generate** the SVG with one command.
4. **Publish** it on your profile.

Pick your system below. Each guide uses the example that matches it, but any system can generate any look.

---

## Windows

<img src="example.svg" width="800" alt="Windows Terminal style" />

Works in **Windows Terminal**, **PowerShell** and **cmd**.

**1. Install Python** (skip if `py --version` already prints a version):

```powershell
winget install Python.Python.3.13
```

Or download it from [python.org](https://www.python.org/downloads/windows/) and tick **"Add python.exe to PATH"** in the installer. Close and reopen the terminal afterwards.

**2. Download the script and the Windows example:**

```powershell
mkdir terminal
cd terminal
curl.exe -O https://raw.githubusercontent.com/ExplorerOf/readme-terminal/main/terminal_svg.py
curl.exe -o terminal.json https://raw.githubusercontent.com/ExplorerOf/readme-terminal/main/example.json
```

Type `curl.exe`, not `curl`: in Windows PowerShell `curl` is a different command.

**3. Edit the config:**

```powershell
notepad terminal.json
```

Make it look like your machine. In JSON a backslash is written twice, so `C:\Users\you>` becomes:

```json
{
  "style": "windows",
  "title": "you / Your Name",
  "prompt": "C:\\Users\\you>",
  "lines": [
    "Microsoft Windows [Version 10.0.26200]",
    "",
    {"cmd": "whoami"},
    "your name · what you do",
    "",
    {"cmd": "type stack.json"},
    "{ \"languages\": [\"TypeScript\", \"Python\"] }"
  ]
}
```

**4. Generate the SVG:**

```powershell
py terminal_svg.py terminal.json terminal.svg
```

Always pass the output file name like this. Don't use `> terminal.svg`: Windows PowerShell 5.1 saves it as UTF-16 and the image breaks.

**5. Preview it** in your browser:

```powershell
start terminal.svg
```

Now [put it on your profile](#put-it-on-your-profile).

---

## Linux

<img src="example-linux.svg" width="800" alt="Ubuntu terminal style" />

Works on Ubuntu, Debian, Fedora, Arch and the rest.

**1. Check Python.** Almost every distro ships it:

```bash
python3 --version
```

If it is missing:

```bash
sudo apt install python3      # Ubuntu, Debian, Mint
sudo dnf install python3      # Fedora
sudo pacman -S python         # Arch, Manjaro
```

**2. Download the script and the Linux example:**

```bash
mkdir terminal && cd terminal
curl -O https://raw.githubusercontent.com/ExplorerOf/readme-terminal/main/terminal_svg.py
curl -o terminal.json https://raw.githubusercontent.com/ExplorerOf/readme-terminal/main/example-linux.json
```

No `curl`? Use `wget` and `wget -O terminal.json ...`.

**3. Edit the config:**

```bash
nano terminal.json
```

The Ubuntu prompt has colors: the user in green and the folder in blue. Each part of `prompt` can have its own color, and parts without one use the theme's `cmd` color:

```json
"prompt": [
  {"text": "you@ubuntu", "color": "#8ae234"},
  {"text": ":"},
  {"text": "~", "color": "#729fcf"},
  {"text": "$ "}
]
```

Run `echo "$USER@$HOSTNAME"` to see your own user and host.

**4. Generate the SVG:**

```bash
python3 terminal_svg.py terminal.json terminal.svg
```

**5. Preview it:**

```bash
xdg-open terminal.svg
```

Now [put it on your profile](#put-it-on-your-profile).

---

## macOS

<img src="example-mac.svg" width="800" alt="macOS Terminal style" />

Works in **Terminal** and **iTerm2**.

**1. Check Python:**

```bash
python3 --version
```

If macOS offers to install the "command line developer tools", accept: that installs Python. With [Homebrew](https://brew.sh) you can also run `brew install python`.

**2. Download the script and the macOS example:**

```bash
mkdir terminal && cd terminal
curl -O https://raw.githubusercontent.com/ExplorerOf/readme-terminal/main/terminal_svg.py
curl -o terminal.json https://raw.githubusercontent.com/ExplorerOf/readme-terminal/main/example-mac.json
```

**3. Edit the config:**

```bash
nano terminal.json
```

Prefer `nano` (or VS Code) over TextEdit: TextEdit turns `"` into curly quotes and the JSON stops working. The default zsh prompt looks like this:

```json
"prompt": [
  {"text": "you@MacBook-Pro"},
  {"text": " ~ ", "color": "#58a6ff"},
  {"text": "% "}
]
```

**4. Generate the SVG:**

```bash
python3 terminal_svg.py terminal.json terminal.svg
```

**5. Preview it** in Safari (Preview doesn't play animations):

```bash
open -a Safari terminal.svg
```

Now [put it on your profile](#put-it-on-your-profile).

---

## Put it on your profile

GitHub shows the README of a special repository on your profile page: the **public repository named exactly like your username** (for `octocat` it is `octocat/octocat`).

1. Create it on GitHub if you don't have it yet, with "Add a README file" ticked.
2. Copy `terminal.svg` into it.
3. Add this line to its `README.md`, where you want the terminal:

   ```html
   <img src="terminal.svg" width="800" alt="Terminal" />
   ```

4. Commit and push:

   ```bash
   git add terminal.svg README.md
   git commit -m "Add animated terminal"
   git push
   ```

No git on this machine? On the repository page use **Add file → Upload files** and drop `terminal.svg` there.

## Let GitHub do it (no Python needed)

With this GitHub Action, you only edit `terminal.json`, even right on github.com or from your phone. GitHub generates and commits `terminal.svg` for you.

1. Put your `terminal.json` in your profile repository.
2. Create `.github/workflows/terminal.yml` in the same repository:

   ```yaml
   name: terminal

   on:
     push:
       paths: ["terminal.json"]
     workflow_dispatch:

   permissions:
     contents: write

   jobs:
     terminal:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v7
         - uses: ExplorerOf/readme-terminal@v1
           with:
             config: terminal.json
             output: terminal.svg
         - name: Commit the SVG if it changed
           run: |
             git config user.name "${{ github.actor }}"
             git config user.email "${{ github.actor_id }}+${{ github.actor }}@users.noreply.github.com"
             git add terminal.svg
             git diff --cached --quiet || (git commit -m "Update terminal.svg" && git push)
   ```

3. Commit. From now on, every change to `terminal.json` updates `terminal.svg` within about a minute. You can also run it by hand under **Actions → terminal → Run workflow**.

Several configs, for example one per language? Repeat the `uses: ExplorerOf/readme-terminal@v1` step once per file and `git add` every SVG.

---

## Config reference

The config is a JSON file. Every option has a default, so the smallest config is just `lines`.

### Lines

| You write | You get |
|-----------|---------|
| `{"cmd": "whoami"}` | The prompt, then `whoami` typed letter by letter |
| `"any text"` | An output line, shown once the command above it is typed |
| `""` | A blank line |

A blinking cursor is added after the last line for you. Spaces are kept as typed, so you can line up columns like a real `ls -l`, `ps` or `tasklist`.

### Prompt

A plain text uses the theme's `cmd` color:

```json
"prompt": "$ "
```

A list of parts gives each part its own color. Parts without `color` use the theme's `cmd` color:

```json
"prompt": [{"text": "you@ubuntu", "color": "#8ae234"}, {"text": ":"}, {"text": "~", "color": "#729fcf"}, {"text": "$ "}]
```

### Replay

By default the animation plays, holds the finished screen for `hold` seconds, and starts over. Set `"loop": false` to play it once and keep the final screen.

### All options

| Key | Default | What it does |
|-----|---------|--------------|
| `style` | `"windows"` | Window look: `"windows"`, `"linux"` or `"mac"` |
| `title` | `"user@host"` | Text in the title bar |
| `prompt` | `"$ "` | Shown before every command: a text or colored parts (see above) |
| `lines` | `[]` | What happens in the terminal (see above) |
| `theme` | green on black | Colors, see below |
| `loop` | `true` | Play again after `hold` seconds; `false` plays once |
| `hold` | `5` | Seconds the finished screen stays before playing again |
| `typing_speed` | `12` | Characters typed per second |
| `pause` | `0.5` | Seconds between the end of a command and its output |
| `width` | `800` | Width in pixels; the height grows with the number of lines |
| `font_size` | `14` | Font size in pixels |
| `line_height` | `21` | Distance between lines in pixels |
| `char_width` | `7.7` | Pixels per character, used to pace the typing (7.7 matches Consolas at 14 px) |

A typo in the config, such as an unknown option, a wrong style, or a negative number, stops the script with a message that says what to fix. Lines too long to fit get a warning.

### Themes

`theme` takes six colors. Any you leave out keep the default.

| Key | Colors |
|-----|--------|
| `bg` | Terminal background |
| `bar` | Title bar |
| `border` | Window border |
| `cmd` | Prompt and typed commands |
| `out` | Output lines |
| `title` | Title bar text |

Ready to copy:

| Look | `"theme"` |
|------|-----------|
| Classic green (default) | `{"bg": "#0c0c0c", "bar": "#202020", "border": "#3a3a3a", "cmd": "#39ff14", "out": "#21c421", "title": "#d0d0d0"}` |
| PowerShell blue | `{"bg": "#012456", "bar": "#202020", "border": "#3a3a3a", "cmd": "#ffffff", "out": "#eeedf0", "title": "#d0d0d0"}` |
| Ubuntu | `{"bg": "#300a24", "bar": "#2c2c2c", "border": "#454545", "cmd": "#eeeeec", "out": "#eeeeec", "title": "#eeeeec"}` |
| GitHub dark | `{"bg": "#0d1117", "bar": "#161b22", "border": "#30363d", "cmd": "#e6edf3", "out": "#8b949e", "title": "#8b949e"}` |

---

## How it works

1. The script lays out every line on one timeline and works out when each one starts. Add or remove a line and everything else moves along with it.
2. Every command sits behind an invisible clipping rectangle. When its turn comes, the prompt appears and the rectangle grows at `typing_speed` characters per second, which looks like typing. Once typed, the clipping opens all the way, so the whole line shows in whatever font the visitor has.
3. Output lines appear one every 0.1 s after `pause`, then the next prompt shows up.
4. Each animation spans the whole cycle and starts over together with the others, so every replay begins on a clean screen.

All of it is SVG `<animate>` (SMIL). Browsers play it even inside an `<img>`, which is how GitHub shows every image in a README.

## Tips and troubleshooting

- **The update is not showing.** GitHub caches images for about five minutes. Point to `terminal.svg?v=2` in your README and bump the number on every update.
- **The image is not moving.** Image viewers like Windows Photos and macOS Preview don't play SVG animations. Open it in a browser.
- **The script stopped with an error about the JSON.** Check for a missing comma, a missing quote, or a single `\` (write `\\`). If you edited on a Mac, check for curly quotes.
- **A line is cut on the right.** Keep lines under about 90 characters at the default 800 px width (Linux and Mac fonts are wider than Consolas), or raise `width`. The script warns you when a line is too long.
- **Fonts.** The text uses the visitor's own monospace font: Consolas, Cascadia Mono, Menlo or the system default.
- **Accents and emoji.** The config is UTF-8, so `ção` and `ñ` work. Emoji also work but are wider than one character and can push aligned columns out of place.
- **Light and dark mode.** The terminal brings its own background, so it looks the same in both GitHub themes.
- **Two languages.** Write one config per language and generate one SVG for each, such as `terminal.svg` and `terminal.en.svg`.
- **Writing to stdout.** Leave out the output file and the SVG goes to stdout, for pipes and `>` on Linux and macOS.

## Development

```bash
python3 test_terminal_svg.py
```

The test renders every `example*.json` and checks that each command starts hidden. It also checks replay, the colored prompt and that bad configs are rejected, and it fails if an example SVG is out of date. After changing the code, regenerate the examples:

```bash
for f in example example-linux example-mac; do python3 terminal_svg.py $f.json $f.svg; done
```

On every push, GitHub runs the same test and also runs the Action itself.

## License

[MIT](LICENSE)
