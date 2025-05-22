# kindle-clips

Process your kindle clips into formatted text, org-mode entries or JSON objects.

## Usage

Use your Kindle 'My Clippings.txt' file as input.

CARE! Using the `-o FILE` or `--output FILE` option will overwrite the given
FILE, without confirmation. This should change in the short term as is not
forgiving to user mistakes.

```
usage: kindle-clips [-h] [-o FILE] [-f {text,org,json}] [-H] [-n] [-b] [-q] file

Convert Kindle highlights into text, org-mode or JSON format.

positional arguments:
  file                  File that contains the Kindle clips.

options:
  -h, --help            show this help message and exit
  -o FILE, --output FILE
                        Write output in FILE, excluding messages. stdout is used by default. CARE:
                        FILES WILL BE OVERWRITTEN WITHOUT CONFIRMATION.
  -f {text,org,json}, --format {text,org,json}
                        Define the format of the output. Could be 'text', 'org' or 'json'. Defaults to
                        'text'. ONLY TEXT IS CURRENTLY SUPPORTED.
  -q, --quiet           Dont't print any message. Even error ones.

types of clips:
  This options define which types of clips will be extracted. If no option is used, all types will
  be extracted; otherwise, only those types selected will.

  -H, --highlights      Clips extracted will contain highlights.
  -n, --notes           Clips extracted will contain notes.
  -b, --bookmarks       Clips extracted will contain bookmarks.

More info at https://github.com/leonardosoteldo/kindle-clips
```

## About

Made this tool to learn the Python language and its standar library. I have made
some tests at unit and integration level. But some e2e testing is lacking.

To run tests install the 'pytest' library in the usend VENV and use `$ pytest
test\_kindle\_clips.py`. Using `pytest` alone or adding options such as `$
pytest -v test\_kindle\_clips.py` is currently giving error messages.
