# Built-in imports
import os

# Third-party dependencies
from pymongo import MongoClient
import requests

# Custom imports
import config


# Bot constants
SEARCH_PARAMS = {'q': 'stars:"<5 AND >1"', 'sort': 'updated'}


# Gloabl variable init
if os.environ.get('PYTHON_ENV', None) is 'production':
    client = MongoClient(config.db['prod'])
else:
    client = MongoClient(config.db['dev'])
db = client.add_a_license_db


def make_request(endpoint, req_type='get', headers={}, params={}, body={}):
    '''Make a HTTP request and return JSON response

    Arguments:
        endpoint: Github endpoint to hit
        req_type: HTTP request type
        headers: Any custom headers that must be sent
        params: 'get' query parameters
        body: 'post' body content
    '''

    if not headers.has_key('Authorization'):
        headers['Authorization'] = ('token %s' % config.github['access_token'])

    url = config.github['base_url'] + endpoint

    if req_type is 'get':
        r = requests.get(url, headers=headers, params=params)
    elif req_type is 'post':
        r = requests.post(url, headers=headers, payload=body)

    try:
        return r.json()
    except e:
        # TODO log this
        return None


def get_repo_contents(author_repo):
    '''Return the json/dict of repo contents

    Arguments:
        author_repo: "author/repo". example: karan/projects
    '''
    results = make_request('/repos/%s/contents' % (author_repo,))
    return results


def file_is_license(contents_obj):
    '''Return True iff passed Github content is a license file
    '''
    if contents_obj.type is not 'file':
        return False

    file_name = contents_obj['name'].lower()
    return True if file_name.startswith('license')


def get_search_results():
    '''Return a list of repos for the search.
    '''
    results = make_request('/search/repositories', params=SEARCH_PARAMS)
    return results.items


def main():
    repos = get_search_results()


if __name__ == '__main__':
    main()
