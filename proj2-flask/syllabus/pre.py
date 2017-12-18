"""
Pre-process a syllabus (class schedule) file. 

"""
import arrow   # Dates and times
import logging
logging.basicConfig(format='%(levelname)s:%(message)s',
                    level=logging.INFO)
log = logging.getLogger(__name__)

base = arrow.now()   # Default, replaced if file has 'begin: ...'

now = base.format("MM/DD/YYYY")

def process(raw):
    """
    Yay Line by line processing of syllabus file.  Each line that needs
    processing is preceded by 'head: ' for some string 'head'.  Lines
    may be continued if they don't contain ':'.  
    """
    field = None
    entry = { }
    cooked = [ ]
    for line in raw:
        line = line.rstrip()
        if len(line) == 0:
            continue
        parts = line.split(':')
        if len(parts) == 1 and field:
            entry[field] = entry[field] + " " +line
            continue
        if len(parts) == 2: 
            field = parts[0]
            content = parts[1]
        else:
            raise ValueError("Trouble with line: '{}'\n".format(line) + 
                "Split into |{}|".format("|".join(parts)))

        if field == "begin":
            try:
                base = arrow.get(content, 'MM/DD/YYYY' )
            except:
                raise ValueError("Unable to parse date {}".format(content))

        elif field == "week":
            if entry:
                cooked.append(entry)
                entry = { }

            start = base.replace(days=(7*(int(content)-1))).format('MM/DD/YYYY')
            end = base.replace(days=(7*(int(content)))).format('MM/DD/YYYY')

            current = 'false'

            if now>=start and now<end:
                current = 'true'

            entry['topic'] = ""
            entry['project'] = ""
            entry['week'] = content
            entry['week_date'] = base.replace(days=(7*(int(content)-1))).format('YYYY-MM-DD')
            entry['current'] = current

        elif field == 'topic' or field == 'project':
            entry[field] = content

        else:
            raise ValueError("Syntax error in line: {}".format(line))

    return cooked

def main():
    f = open("data/schedule.txt", encoding="utf8")
    parsed = process(f)
    print(parsed)

if __name__ == "__main__":
    main()
