import requests

if __name__ == '__main__':

    jwt_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMDE3Nzc5MDQ2NTAyMzAzMzA3NzgiLCJuYW1lIjoiVyBLIEsiLCJleHAiOjE2ODc3MDg0Nzd9.g84_HupTV99Tbrjx4tMw3VqI3H6EVRmiSAA3vKsUWmM'

    headers = {
        'Authorization': f'Bearer {jwt_token}'
    }

    response = requests.get('http://localhost:5000/api/auth/test', headers=headers)

    if response.status_code == 200:
        print(response.text)
    else:
        print(f'Request failed with status code {response.status_code}')