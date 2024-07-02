import json

if __name__ == '__main__':
    with open('oauth.json', "r") as f:
        d = json.load(f)
        print(d)