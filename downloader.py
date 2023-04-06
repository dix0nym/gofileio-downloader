import argparse
import hashlib

from pathlib import Path

import requests
from tqdm import tqdm

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0'

def createAccount(session):
    response_account = session.get('https://api.gofile.io/createAccount')
    if response_account.status_code == 200:
        json_data = response_account.json()
        if 'data' in json_data and 'token' in json_data['data']:
            return json_data['data']['token']
        else:
            exit(f'failed to create account - missing token {json_data} - exiting')
    exit(f'failed to create account - {response_account.status_code} - exiting')

def getFileList(session, contentId, token, websiteToken='12345'):
    params = {'contentId': contentId, 'token': token, 'websiteToken': websiteToken}
    response = session.get('https://api.gofile.io/getContent', params=params)
    if response.status_code == 200:
        json_data = response.json()
        if json_data['status'] == 'ok':
            return json_data
        else:
            exit(f'failed to get files for {contentId} - {json_data}')
    exit(f'failed to get files for {contentId} - {response.status_code}')

def getHash(path):
    if not path.exists():
        return None
    hash_md5 = hashlib.md5()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def downloadFile(session, data_obj, filepath):
    with session.get(data_obj['link'], stream=True) as r:
        file_size = int(r.headers.get('content-length', 0))
        with filepath.open('wb+') as f:
            with tqdm.wrapattr(f, "write", miniters=1, desc=filepath.name, total=file_size) as fout:
                for chunk in r.iter_content(chunk_size=8192):
                    fout.write(chunk)
    
def processDataObj(session, data_obj, filepath):
    expectedHash = data_obj["md5"]
    if filepath.exists():
        # check hash
        if getHash(filepath) == expectedHash:
            print(f"[!] file {data_obj['name']} already exists - skip")
            return
        else:
            print(f"[!] file {data_obj['name']} hash mismatch (expected: {expectedHash})")
            filepath.unlink()
    for i in range(3):
        print(f"[+] download attempt {i}/3 - {data_obj['name']}")
        downloadFile(session, data_obj, filepath)
        if getHash(filepath) != expectedHash:
            filepath.unlink()
        else:
            break

def main():
    parser = argparse.ArgumentParser(description='Gofile.io downloader')
    parser.add_argument('url', metavar='URL', type=str, help='url to download - e.g. https://gofile.io/d/XXXXXX')
    parser.add_argument('-u', '--user-agent', type=str, help='custom user-agent-string')
    args = parser.parse_args()
    
    url = args.url
    session = requests.Session()
    session.headers.update({'User-Agent': args.user_agent or USER_AGENT})
    # get cookies
    session.get(url)
    # create account
    token = createAccount(session)
    # extract accountToken
    session.cookies.set('accountToken', token)
    # get contentId
    contentId = url[url.rfind('/') + 1:]
    # request filelist using contentId and token in session
    data = getFileList(session, contentId, token)
    print(f"[!] found {len(data['data']['contents'].keys())} files")

    # prepare download folder
    outFolder = Path('./output', contentId)
    outFolder.mkdir(parents=True, exist_ok=True)

    contents = data['data']['contents']
    # iterate over all available files
    for _, data_obj in contents.items():
        filepath = Path.joinpath(outFolder, data_obj['name'])
        processDataObj(session, data_obj, filepath)

if __name__ == "__main__":
    main()
