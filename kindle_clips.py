from dataclasses import dataclass
from datetime import date, time
from re import search, IGNORECASE
import json
import argparse

### CLASSES
######################################################################

@dataclass
class RawClip:
    source: str
    info: str
    blank: str
    content: str
    delimiter: str

@dataclass
class Clip:
    type: str
    source: str
    page: list[int]
    location: list[int]
    date: date | None
    time: time | None
    content: str

@dataclass
class Extraction:
    highlights: list[Clip]
    notes: list[Clip]
    bookmarks: list[Clip]
    unparsed: list[tuple[RawClip, int]]

### CLIPS PARSING
######################################################################

# TODO: org-mode formatting
# TODO: JSON formatting
# TODO: add basic sorting for output
# TODO: move file handling from the parsing function to the main logic

def parse_rawclips_file(file: str) -> Extraction:
    """Parse a given file (a path in the form of a str) into a Extraction.

    Every kindle clip, as existing in the kindle's 'My Clippings.txt'
    file, consists in:
      - a line with the source's title and author;
      - a line with page, location, date and time (of the clip) information;
      - a blank line;
      - a line with the hightlighted text or annotated commentary and
      - a delimiter line made by repeated equal signs: '=========='

    Every line is read, stripped of the newline character, and stored
    as their correspondent RawClip's field. The RawClip is evaluated
    to check if It's a highlight or a note. Finally, the RawClip is
    passed to the 'parse_rawclip()' function and stored as a Clip in a
    list to be returned as part or the output Extraction.

    An example of a raw kindle clip as seen in a 'My clippings.txt'
    file:

    > Common LISP: A Gentle Introduction to Symbolic Computation (David S. Touretzky)
    > - Your Highlight on page 46 | Location 694-694 | Added on Sunday, August 27, 2023 1:37:08 PM
    >
    > The length of a list is the number of elements it has
    > ==========

    """

    highlights: list[Clip]              = []
    notes: list[Clip]                   = []
    bookmarks: list[Clip]               = []
    unparsed: list[tuple[RawClip, int]] = []
    current_clip: list[str]             = []
    line_cnt: int                       = 0
    cnt: int                            = 1

    with open(file, mode='r', encoding='UTF-8', newline='\n') as f:

        for line in f:

            # The fifth line of a clip should be a delimiter. Collect
            # the fivelines, create a RawClip and parse it into a Clip.
            if cnt >= 5:
                rclip = RawClip(current_clip[0],
                                current_clip[1],
                                current_clip[2],
                                current_clip[3],
                                line.removesuffix('\n'))

                clip = parse_rawclip(rclip)

                # Collect the clip/rclip into the corresponding list
                match clip.type:
                    case 'highlight':
                        highlights.append(clip)
                    case 'note':
                        notes.append(clip)
                    case 'bookmark':
                        bookmarks.append(clip)
                    case 'unparsed':
                        unparsed.append((rclip, line_cnt))
                    case _:
                        raise ValueError

                # Clear the lines collector and update counters
                current_clip.clear()
                cnt = 1
                line_cnt += 1

            else:
                # Collect the lines
                current_clip.append(line.removesuffix('\n'))
                line_cnt += 1
                cnt += 1

        else:
            return Extraction(highlights, notes, bookmarks, unparsed)

def parse_rawclip(rawclip: RawClip) -> Clip:
    """Parse a RawClip and generate a Clip object.

    See 'parse_clips-file() documentation for more information about
    how Kindle stores the clips and how the parsing is done."""
    return Clip(get_rawclip_type(rawclip),
                rawclip.source,
                parse_page_info(rawclip.info),
                parse_location_info(rawclip.info),
                parse_date_info(rawclip.info),
                parse_time_info(rawclip.info),
                rawclip.content)

def get_rawclip_type(rclip: RawClip) -> str:
    "Checks rclip type and return 'highlight' or 'note' string."
    if  rclip.info.startswith('- Your Highlight'):
        return 'highlight'
    elif rclip.info.startswith('- Your Note'):
        return 'note'
    elif rclip.info.startswith('- Your Bookmark'):
        return 'bookmark'
    else:
        return 'unparsed'

def parse_page_info(string: str) -> list[int]:
    "Parse the page information as given in Clip.info."
    match = search(r'pages? ([0-9]+)-([0-9]+)|page ([0-9]+)',
                      string, IGNORECASE)
    if match is None:
        return []
    else:
        return [int(page) for page in match.groups() if page is not None]

def parse_location_info(string: str) -> list[int]:
    "Parse the location information as given in Clip.info."
    match = search(r'Location ([0-9]+)-([0-9]+)|Location ([0-9]+)',
                    string, IGNORECASE)
    if match is None:
        return []
    else:
        return [int(loc) for loc in match.groups() if loc is not None]

MONTHS: dict = {
    "january"    : 1,
    "february"   : 2,
    "march"      : 3,
    "april"      : 4,
    "may"        : 5,
    "june"       : 6,
    "july"       : 7,
    "august"     : 8,
    "september"  : 9,
    "october"    : 10,
    "november"   : 11,
    "december"   : 12
}

def parse_date_info(string: str) -> date | None:
    "Parse the date information as given in Clip.info."
    match = search(r'Added on [a-z]+, ([a-z]+) ([0-9]{1,2}), ([0-9]{4})',
                      string, IGNORECASE)
    if match is None:
        return None
    else:
        year: int  = int(match.group(3))
        month: int = MONTHS[match.group(1).lower()]
        day: int   = int(match.group(2))
        return date(year, month, day)

def parse_time_info(string: str) -> time | None:
    "Parse the time information as given in Clip.info."
    match = search(r'([0-9]{1,2}):([0-9]{1,2}):([0-9]{1,2}) ([AMP]+)$',
                      string, IGNORECASE)
    if match is None:
        return None
    else:
        hour: int     = int(match.group(1))
        minutes: int  = int(match.group(2))
        seconds: int  = int(match.group(3))
        period: str   = match.group(4).upper()

        # Convert from 12h time to 24h time
        # TODO: Kindle uses 12am for noon or midnight?
        if period == 'PM' and hour != 12:
            hour += 12
        elif period  == 'AM' and hour == 12:
            hour -= 12

        return time(hour, minutes, seconds)

### OUTPUT FORMATTING AND MESSASGING
######################################################################

def format_clips(clips: list[Clip], format: str) -> str:
    "Return a string with given Clips properly formatted."

    match format:
        case 'text':
            return text_formatter(clips)
        case 'org':
            return org_formatter(clips)
        case 'json':
            return json_formatter(clips)
        case _:
            raise ValueError('Given format is not defined.')

def text_formatter(clips: list[Clip]) -> str:
    """Process a list of clips into a pretty text format."""

    columns: int = 70
    delimiter: str = '-' * columns + '\n'
    result: list[str] = []

    for clip in clips:

        c = ''.join(["Source: {}\n".format(clip.source),
                     "Page: {}\n".format(pages_and_loc_to_str(clip.page)),
                     "Location: {}\n".format(pages_and_loc_to_str(clip.location)),
                     "Creation: {} | {}\n".format(str(clip.date), str(clip.time)),
                     "{}:\n\n".format(clip.type.capitalize),
                     clip.content + '\n',
                     delimiter])

        result.append(c)

    return delimiter + delimiter.join(result) + delimiter

def org_formatter(clips: list[Clip]) -> str:
    """Process a list of clips into a pretty org-mode format."""

    delimiter: str = '\n'
    result: list[str] = []

    for clip in clips:

        c = '\n'.join(["* {}\n".format(clip.source), # org-mode header
                       "  :PROPERTIES:",
                       "  :Source: {}".format(clip.source),
                       "  :Page: {}".format(pages_and_loc_to_str(clip.page)),
                       "  :Location: {}".format(pages_and_loc_to_str(clip.location)),
                       "  :Date: {}".format(str(clip.date)),
                       "  :Time: {}".format(str(clip.time)),
                       "  :Type: {}:".format(clip.type),
                       "  :END:\n",
                       clip.content,
                       delimiter])

        result.append(c)

    return delimiter + delimiter.join(result)

def json_formatter(clips: list[Clip]) -> str:
    """Process a list of clips into json format."""

    result: list[dict] = []

    for clip in clips:

        c = {"source" : clip.source,
             "page" : clip.page,
             "location" : clip.location,
             "date" : str(clip.date),
             "time" : str(clip.source),
             "type" : clip.type,
             "content" : clip.content}

        result.append(c)

    return json.dumps(result, indent=4)

def pages_and_loc_to_str(pp: list[int] | None) -> str:
    "Convert pages and locations into a pretty string."

    if pp is None:
        return 'no data'

    else:
        pp_len: int = len(pp)

        if pp_len == 0:
            return 'no data'
        elif pp_len == 1:
            return str(pp[0])
        elif pp_len == 2:
            return str(pp[0]) + '-' + str(pp[1])
        else:
            return ''.join(str(i) + ', ' for i in pp).removesuffix(', ')

def print_parsing_errors(rclips: list[tuple[RawClip, int]]) -> None:
    """Print messages about all RawClips that couldn't be parsed.

    These errors are collected by the function 'parse_raw_clips_file()."""
    for rclip, line_num in rclips:
        print_rawclip_parsing_error(rclip, line_num)
    else:
        return

def print_rawclip_parsing_error(rclip: RawClip, line_num: int) -> None:
    "Print message about RawClip that couldn't be parsed correctly."
    print("Got an error while processing your Kindle clips file.")
    print(f"The clip ending at line {line_num} couldn't be parsed:")
    print(f'    > {rclip.source}')
    print(f'ERR > {rclip.info}')
    print(f"    > {rclip.blank}")
    print(f'    > {rclip.content}')

    return

def print_extraction_messages(is_quiet: bool, extraction: Extraction,
                              types: list[str]) -> None:
    "Print information messages of the extracted Clips."

    if is_quiet:
        return

    elif not types:
        print(f"Found {len(extraction.highlights)} highlights.")
        print(f"Found {len(extraction.notes)} notes.")
        print(f"Found {len(extraction.bookmarks)} bookmarks.")
        return

    else:
        if 'highlights' in types:
            print(f"Found {len(extraction.highlights)} highlights.")

        if 'notes' in types:
            print(f"Found {len(extraction.notes)} notes.")

        if 'bookmarks' in types:
            print(f"Found {len(extraction.bookmarks)} bookmarks.")

        return

### ARGUMENT PARSING AND MAIN LOGIC
######################################################################

parser = argparse.ArgumentParser(
    prog='kindle-clips',
    description='''Convert Kindle highlights into text, org-mode or
    JSON format.''',
    epilog='More info at https://github.com/golfeado/kindle-clips')

parser.add_argument('file', type=str,
                    help='File that contains the Kindle clips.')

parser.add_argument('-o', '--output', metavar='FILE', type=str,
                    default=None, help='''Write output in FILE,
                    excluding messages. stdout is used by
                    default. CARE: FILES WILL BE OVERWRITTEN WITHOUT
                    CONFIRMATION.''')

parser.add_argument('-f', '--format', type=str, choices=['text', 'org', 'json'],
                    default='text', help="""Define the format of the
                    output. Could be 'text', 'org' or 'json'. Defaults
                    to 'text'.""")

types_of_clip = parser.add_argument_group('types of clips', '''This
options define which types of clips will be extracted. If no option is
used, all types will be extracted; otherwise, only those types
selected will.''')

types_of_clip.add_argument('-H', '--highlights', dest='types',
                           action='append_const', const='highlights',
                           help='''Clips extracted will contain
                           highlights.''')

types_of_clip.add_argument('-n', '--notes', dest='types',
                           action='append_const', const='notes',
                           help='''Clips extracted will contain
                           notes.''')

types_of_clip.add_argument('-b', '--bookmarks', dest='types',
                           action='append_const', const='bookmarks',
                           help='''Clips extracted will contain
                           bookmarks.''')

parser.add_argument('-q', '--quiet', action='store_true',
                    help="Dont't print any message. Even error ones.")

args = parser.parse_args()

if __name__ == '__main__':

    # Initial message
    if not args.quiet: print(f"Processing '{args.file}'.")

    # Get extracted clips
    extraction: Extraction = parse_rawclips_file(args.file)
    results: list[Clip] = []

    # Print messages about errors, extracted and requested clips
    if not args.quiet: print_parsing_errors(extraction.unparsed)
    print_extraction_messages(args.quiet, extraction, args.types)

    # Define which type of the extracted clips are needed by request
    # of the user; the others are not used
    if not args.types:
        results = extraction.highlights + extraction.notes + extraction.bookmarks

    else:
        if 'highlights' in args.types:
            results.extend(extraction.highlights)

        if 'notes' in args.types:
            results.extend(extraction.notes)

        if 'bookmarks' in args.types:
            results.extend(extraction.bookmarks)

    # Print to stdout or write to requested file
    if args.output is None:
        print(format_clips(results, args.format))
    else:
        with open(args.output, mode='w', encoding='utf-8') as file:
            file.write(format_clips(results, args.format))
