# Built-in imports
import json
import logging
import os
import random
import time

# Third-party dependencies
import dataset
import requests

# Custom imports
try:
    import config
except:
    import config_example as config


# Bot constants
SEARCH_PARAMS = {'q': 'stars:"<5 AND >1"', 'sort': 'updated'}

# Name qualifiers for license files
LICENSE_FILE_NAMES = [
    'license',
    'epl-',
    'cpl-',
    'copying'
]


# Gloabl variable init
db = None
if os.environ.get('PYTHON_ENV', None) is 'production':
    db = dataset.connect(config.db['prod'])
else:
    db = dataset.connect(config.db['dev'])
table = db['repos']

logging.basicConfig(filename='logger.log',
                    level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def make_request(endpoint, req_type='get', headers={}, params={}, text=False):
    '''Make a HTTP request and return JSON response

    Arguments:
        endpoint: Github endpoint to hit
        req_type: HTTP request type
        headers: Any custom headers that must be sent
        params: 'get' query parameters or 'post' body
        text: Returns raw text response if True
    '''

    logging.info('Making HTTP request: %s %s' % (req_type, endpoint))
    logger.debug('params: %s' % params)

    if not headers.has_key('Authorization'):
        headers['Authorization'] = ('token %s' % config.github['access_token'])

    url = config.github['base_url'] + endpoint

    if req_type is 'get':
        r = requests.get(url, headers=headers, params=params)
    elif req_type is 'post':
        r = requests.post(url, headers=headers, data=json.dumps(params))

    try:
        if r.status_code in (200, 201):
            if text:
                return r.text
            return r.json()
        else:
            logger.warn('HTTP request failed: %s' % r.text)
            return {}
    except Exception, e:
        logger.error('HTTP request failure: %s' % e)
        return {}


def get_repo_contents(author_repo):
    '''Return the json/dict of repo contents

    Arguments:
        author_repo: "author/repo". example: karan/projects
    '''
    return make_request('/repos/%s/contents' % (author_repo,))


def get_readme_content(contents):
    '''Returns the content (file) object that represents a README file.

    Arguments:
        contents: The list of dict contents as returned by Github
    '''
    for content_file in contents:
        if content_file['name'].lower().startswith('readme'):
            return content_file
    return {}


def file_is_license(contents_obj):
    '''Return True if passed Github content is a license file

    Arguments:
        contents_obj: One dict as returned from repo content
    '''
	is_found = -1
    file_name = contents_obj['name'].lower()
    for valid_name in LICENSE_FILE_NAMES:
        if file_name.startswith(valid_name):
            return file_has_GPL(file_name);
    return False


def file_has_GPL(file_obj):
    '''Return True if the passed content object has "GNU" in content.

    file_obj: One dict as returned from repo content which is the file being probed
    '''
    logger.debug('Checking README: %s' % readme_obj)
    if file_obj is None:
        return False

    file_content_endpoint = file_obj['url'].split(config.github['base_url'])[1]
    headers = {'Accept': 'application/vnd.github.v3.raw'}

    file_content = make_request(file_content_endpoint, headers=headers,
                                  text=True)
    file_content = file_content.lower()
	
	is_found = -1
	
	is_found = file_content.find("GNU General Public License");
	
	is_found = file_content.find("GPL");
	
    return is_found > -1


def get_search_results():
    '''Return a list of repos for the search.
    '''
    results = make_request('/search/repositories', params=SEARCH_PARAMS)
    return results.get('items', [])


def has_seen_repo(repo_id):
    '''Return True if we have previously seen this repo.

    Arguments:
        repo_id: The repo id given by Github API
    '''
    repo = table.find_one(repo_id=repo_id)
    return bool(repo)


def create_issue(author_repo):
    '''Creates an issue requesting the user to add a license.

    Arguments:
        author_repo: "author/repo". example: karan/projects
    '''
    issue_body = '%s\n\n%s' % (random.choice(config.issue['body']),
                               config.issue['call_to_action'])
    body = {
        'title': random.choice(config.issue['titles']),
        'body': issue_body
    }
    return make_request('/repos/%s/issues' % (author_repo,), 'post',
                        params=body)


def main():
    repos = get_search_results()
    logger.info('Got repos: %s' % len(repos))

    for repo in repos:
        logger.debug('Processing repo: %s' % repo)

        star_count = repo.get('stargazers_count')
        if star_count is 0 or star_count > 5:
            logger.info('Skipping stars out of range: %s' % str(star_count))
            continue

        if has_seen_repo(repo['id']):
            logger.info('Already seen repo: %s' % str(repo['id']))
            continue

        # Get the files in this repo
        repo_contents = get_repo_contents(repo['full_name'])

        logger.debug('Repo contents: %s' % repo_contents)

        found_license = False
        # Check to see if there's a license file in the repo
        for repo_file in repo_contents:
            logger.info('Processing file: %s' % repo_file['name'])

            if file_is_license(repo_file):
                # Has a license, log in db and skip
                row = table.insert(dict(repo_id=repo['id'],
                                        repo_name=repo['name'],
                                        repo_full_name=repo['full_name'],
                                        has_license=True,
                                        license_file=repo_file['name'],
                                        raw_repo_dump=json.dumps(repo)))
                logger.info('Is a license file. Saved in db, row=%s' % str(row))
                found_license = True
                break

        # License file found, skip to next file
        if found_license:
            continue

        # No explicit license file, check if readme has license info
        readme_content_obj = get_readme_content(repo_contents)

        logger.info('Readme file: %s' % readme_content_obj.get('name'))

        if file_has_GPL(readme_content_obj):
            # Has a license, log in db and skip
            row = table.insert(dict(repo_id=repo['id'],
                                    repo_name=repo['name'],
                                    repo_full_name=repo['full_name'],
                                    has_license=True,
                                    license_file=readme_content_obj['name'],
                                    raw_repo_dump=json.dumps(repo)))
            logger.info('Readme has GPL. Saved in db, row=%s' % str(row))
        else:
            logger.info('GPL not found. Creating issue.')
            # Create an issue and log it in the database
            result = create_issue(repo['full_name'])
            issue_url = result.get('html_url', None)

            logger.info('Issue URL = %s' % issue_url)

            row = table.insert(dict(repo_id=repo['id'],
                                    repo_name=repo['name'],
                                    repo_full_name=repo['full_name'],
                                    has_license=False,
                                    issue_url=issue_url,
                                    raw_repo_dump=json.dumps(repo)))
            logger.info('Issue created. Saved in db, row=%s' % str(row))

            logger.info('Sleeping for 2 minutes')
            time.sleep(120)


if __name__ == '__main__':
    main()
