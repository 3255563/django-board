import re


from django.core.exceptions import ObjectDoesNotExist


import board.models

ESCAPING_TABLE = [
    ('\&gt;', '&gt;'),
    ('\*', '*'),
    ('\`', '`'),
    ('\_', '_'),
    ('\~', '~'),
    ('\%', '%'),
    ('\-', '-'),
]


def make_formatter_by_regex(pattern, repl, text, flags=0):
    def formatter():
        formatted_text = re.sub(pattern, repl, text, flags=flags)
        return(formatted_text)
    return(formatter)


def format_quotes(text):
    formatted_lines = []

    for line in text.splitlines():
        if line.startswith('&gt; '):
            line = '<blockquote>' + line[5:] + '</blockquote>'
        elif line.startswith('&gt;') and line[4:8] != '&gt;':
            line = '<blockquote>' + line[4:] + '</blockquote>'
        formatted_lines.append(line)

    return("\n".join(formatted_lines))


def format_bold(text):
    formatter = make_formatter_by_regex(
        '\*\*(?P<boldtext>.+?(?=\*\*))\*\*',  # **BOLD TEXT**
        '<strong>\g<boldtext></strong>', text, flags=re.DOTALL)
    return(formatter())


def format_emphasized(text):
    formatter = make_formatter_by_regex(
        r"(?P<before>([^\\]|\A))\*(?P<emphasized>[^\*]+)\*",  # *EM*
        '\g<before><em>\g<emphasized></em>', text)
    return(formatter())


def format_underline(text):
    formatter = make_formatter_by_regex(
        '__(?P<underlined>.+?(?=__))__',  # __underlined__
        '<u>\g<underlined></u>', text, flags=re.DOTALL)
    return(formatter())


def format_strikethrough(text):
    formatter = make_formatter_by_regex(
        '~~(?P<strikethrough>.+?(?=~~))~~',
        '<del>\g<strikethrough></del>', text, flags=re.DOTALL)
    return(formatter())


def format_inline_code(text):
    formatter = make_formatter_by_regex('`(?P<code>.+)`',  # `CODE`
                                        '<code>\g<code></code>', text)
    return(formatter())


def format_multiline_code(text):
    formatter = make_formatter_by_regex(  # ``CODE
        '```(?P<code>(.|\n)+)```',         # ...``
        '<pre><code>\g<code></code></pre>', text, flags=re.DOTALL)
    return(formatter())


def format_spoilers(text):
    formatter = make_formatter_by_regex(
        '%%(?P<spoilered>.+?(?=%%))%%',  # %%spoiler (\n)%%
        '<span class="spoiler">\g<spoilered></span>',
        text, flags=re.DOTALL)
    return(formatter())


def format_hyphens_to_dashes(text):
    formatter = make_formatter_by_regex(
        '(?P<before>\s|\A)-(?P<after>\s|\Z)',  # "a - a" or "- a"
        '\g<before>–\g<after>', text)  # fd
    return(formatter())


def format_references(text):
    referenced_text = text[:]

    for match in re.findall('&gt;&gt;\d+', text):
        ref = int(match[8:])  # saving referenced post's id

        try:
            thread = board.models.Thread.objects.get(id=ref)
            thread_url = thread.get_absolute_url()
            ref_url = thread_url + '#' + str(ref)  # final reference url

            repl = '<a href="{}">{}</a>'.format(ref_url, match)
            referenced_text = referenced_text.replace(match, repl)

        except ObjectDoesNotExist:
            try:
                reply = board.models.Reply.objects.get(id=ref)
                thread_url = reply.thread.get_absolute_url()
                ref_url = thread_url + '#' + str(ref)

                repl = '<a href="{}">{}</a>'.format(ref_url, match)
                referenced_text = referenced_text.replace(match, repl)

            except ObjectDoesNotExist:
                pass

    return(referenced_text)


def escape_formatting(text):
    for unescaped, escaped in ESCAPING_TABLE:
        text = text.replace(unescaped, escaped)
    return(text)
