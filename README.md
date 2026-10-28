# readme-terminal

Animated terminal window for your GitHub profile README, generated as a single SVG file.
No dependencies, no external service, nothing to host: the SVG lives in your repo.

![Windows style](example.svg)

![macOS style](example-mac.svg)

Commands are "typed" one after another, outputs appear when the command finishes, and a cursor blinks at the end.
Windows and macOS window styles are included; colors are configurable.

## Usage

```bash
python terminal_svg.py example.json > terminal.svg
```

Then in your README:

```html
<img src="terminal.svg" width="800" alt="Terminal" />
```

## Config

```json
{
  "style": "windows",
  "title": "Explorer_Of / Gustavo Kogien Caraski",
  "prompt": "C:\\Users\\Explorer_Of>",
  "lines": [
    {"cmd": "whoami"},
    "Gustavo Kogien Caraski · back-end developer",
    "",
    {"cmd": "type stack.json"},
    "{ \"languages\": [\"TypeScript\", \"Python\"] }"
  ]
}
```

| Key | Default | Meaning |
|-----|---------|---------|
| `style` | `windows` | `windows` or `mac` window chrome |
| `title` | `user@host` | Text in the title bar |
| `prompt` | `$ ` | Prompt shown before each command |
| `lines` | `[]` | `{"cmd": "..."}` is typed; a plain string is printed as output; `""` is a blank line |
| `typing_speed` | `12` | Characters per second |
| `pause` | `0.5` | Seconds between a command and its output |
| `width` | `800` | SVG width in px; height follows the number of lines |
| `theme` | green on black | `bg`, `bar`, `border`, `cmd`, `out`, `title` colors |
| `char_width` | `7.7` | Px per character, used to size the typing animation |

See [example.json](example.json) and [example-mac.json](example-mac.json).

## Tips

- GitHub caches raw files for about five minutes. If an update does not show up, reference `terminal.svg?v=2` and bump the number.
- Keep lines under about 95 characters at the default width, or raise `width`.
- Text uses the viewer's monospace font. If a line looks slightly cut while typing, adjust `char_width`.

## License

MIT
