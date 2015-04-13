import os


github = dict(
    client_id = os.environ.get('GITHUB_CLIENT_ID', ''),
    client_secret = os.environ.get('GITHUB_CLIENT_SECRET', ''),
    access_token = os.environ.get('GITHUB_SECRET_TOKEN', ''),
    base_url = 'https://api.github.com'
)

db = dict(
    prod = 'sqlite:///<db_name>.db',
    dev = 'sqlite:///<db_name>.db'
)

issue = dict(
    titles = [
        'Please free this software',
        'GPL missing from repo',
        'Project is not free as in freedom',
        'Add the GPL'
    ],
    body = [
        ('Without the GPL, this project isn\'t free as in freedom and no one can '
         'use the code.'),
        ('This repo is missing the GNU General Public License. Without the GPL, all code is '
         'copyright the author and may not be used by anyone else.'),
		('I\'d just like to interject for a moment.'
		 '\n\nWhat you\'re referring to as Linux, is in fact, GNU/Linux, '
		  'or as I\'ve recently taken to calling it, GNU plus Linux. Linux '
		  'is not an operating system unto itself, but rather another free component '
		  'of a fully functioning GNU system made useful by the GNU corelibs, shell '
		  'utilities and vital system components comprising a full OS as defined by POSIX.')
    ],
    call_to_action = ('Please switch to the GPL and elminate all non-free code '
					  'as soon as possible.'
                      '\n\n'
                      'A PSA called [**Free Your Software Please!**]'
                      '(https://www.gnu.org/gnu/manifesto.html)')
)
