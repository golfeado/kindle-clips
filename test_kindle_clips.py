import pytest
from kindle_clips import *

highlight_rawclip: RawClip = RawClip(
    'Ciudad, urbanización y urbanismo en el siglo XX venezolano (Venezuela siglo XX nº 3) (Spanish Edition) (Almandoz Marte, Arturo)',
    '- Your Highlight on pages 40-45 | Location 542-546 | Added on Thursday, November 17, 2022 12:55:54 PM',
    '',
    'La Venezuela que ingresa al siglo XX, asolada...',
    '==========')

note_rawclip: RawClip = RawClip(
    'Common LISP: A Gentle Introduction to Symbolic Computation (Dover Books on Engineering) (David S. Touretzky)',
    '- Your Note on page 217 | Location 3326 | Added on Friday, September 29, 2023 2:00:29 PM',
    '',
    'Recursion en la vida real',
    '==========')

corrupted_rawclip: RawClip = RawClip(
    'Common LISP: A Gentle Introduction to Symbolic Computation (Dover Books on Engineering) (David S. Touretzky)',
    '- Your Clip on page 217 | Location 3326 | Added on Friday, September 29, 2023 2:00:29 PM',
    '',
    'Recursion en la vida real',
    '==========')

def test_get_rawclip_type():
    assert get_rawclip_type(highlight_rawclip) == 'highlight'
    assert get_rawclip_type(note_rawclip) == 'note'
    # with pytest.raises(RuntimeError):
    #     get_rawclip_type(corrupted_rawclip)

def test_parse_rawclip():
    highlight = parse_rawclip(highlight_rawclip)
    assert highlight.source    == highlight_rawclip.source
    assert highlight.page      == [40, 45]
    assert highlight.location  == [542, 546]
    assert highlight.date      == date(2022, 11, 17)
    assert highlight.time      == time(12, 55, 54)
    assert highlight.content   == 'La Venezuela que ingresa al siglo XX, asolada...'

def test_parse_rawclips_file():
    testing_clips = parse_rawclips_file('testing_clips.txt')
    # Tests for highlights extraction
    highlights = testing_clips.highlights
    assert all(map(lambda c: c.source != note_rawclip.source, highlights))
    assert len(highlights)         == 4
    assert highlights[0].page      == [40]
    assert highlights[0].location  == [542, 546]
    assert highlights[3].source    == 'Python (Python Documentation Authors)'
    assert highlights[3].content.startswith('To use formatted string literals')
    assert highlights[3].date      == date(2024, 5, 10)
    assert highlights[3].time      == time(18, 45, 50)
    # Tests for notes extraction
    notes = testing_clips.notes
    assert all(map(lambda c: c.source != highlight_rawclip.source, notes))
    assert len(notes)         == 3

def test_parse_time_info():
    assert parse_time_info('11:59:59 PM') == time(23, 59, 59)
    assert parse_time_info('12:00:00 AM') == time(0, 0, 0)
    assert parse_time_info('12:00:01 AM') == time(0, 0, 1)
    assert parse_time_info('11:59:59 AM') == time(11, 59, 59)
    assert parse_time_info('12:00:00 PM') == time(12, 0, 0)
    assert parse_time_info('12:00:01 PM') == time(12, 0, 1)

def test_pages_and_loc_to_str():
    assert pages_and_loc_to_str([]) == 'no data'
    assert pages_and_loc_to_str([1]) == '1'
    assert pages_and_loc_to_str([1, 5]) == '1-5'
    assert pages_and_loc_to_str([1, 5, 10]) == '1, 5, 10'
