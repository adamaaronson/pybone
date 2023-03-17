# pybone

Trombone optimizer, written in Python.

## How to use

Run the command:

```
python3 pybone.py -m [method] [notes...]
```

Using any of the following methods:

| Name | Description |
|---|---|
| distance (default) | Minimize total slide movement distance |
| direction | Minimize slide direction changes |
| gliss | Minimize partial changes to optimize for glissando |
| legato | Maximize partial changes to optimize for natural legato |

Each note should be written in scientific pitch notation, with a letter name, optionally followed by a sharp (`#`) or a flat (`b`), followed by an octave number.

## Examples

```
python3 pybone.py Bb3 B3 C4 D4

Bb3     5th-0.137
B3      4th-0.137
C4      3rd-0.137
D4      4th+0.0196
```

```
python3 pybone.py -m direction C#4 D4 C#4

C#4     5th+0.0196
D4      4th+0.0196
C#4     2nd-0.137
```

```
python3 pybone.py -m gliss C#4 F4 C4

C#4     5th+0.0196
F4      1st+0.0196
C4      6th+0.0196
```

```
python3 pybone.py -m legato C4 D4 E4 D4 C4

C4      3rd-0.137
D4      4th+0.0196
E4      5th-0.312
D4      4th+0.0196
C4      3rd-0.137
```