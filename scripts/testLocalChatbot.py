import requests
import argparse
import traceback
import json

local_api = 'http://localhost:{}/api/chatroom/v1?sessionId={}&text={}'


def main(args):
    try:
        r = requests.get(local_api.format(args.port,args.sessionId,args.text))
        if r.status_code != 200:
            print(r.url)
            print("bad connect")
        print(json.loads(r.text))
    except:
        traceback.print_exc()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--text',type=str,required=True)
    parser.add_argument('--sessionId', type=int, required=True)
    parser.add_argument('--port',type=int,required=True)
    args = parser.parse_args()
    main(args)