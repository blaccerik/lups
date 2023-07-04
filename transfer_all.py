import subprocess
import os


# (r"C:\Users\erik\WebstormProjects\lups\lups\dist\lups\*",
#  f"{name}@{ip}:/var/www/html"),

def main():
    key = r"C:\Users\erik\desktop\erikfinal.pem"
    ip = "52.174.181.107"
    name = "erik"

    commands = [

        (r"C:\Users\erik\PycharmProjects\lups\data",
         f"{name}@{ip}:/var/www/data"),

        # (r"C:\Users\erik\PycharmProjects\lups\celeryr",
        #  f"{name}@{ip}:/var/www/"),
        #
        # (r"C:\Users\erik\PycharmProjects\lups\flaskr",
        #  f"{name}@{ip}:/var/www/"),

        (r"C:\Users\erik\PycharmProjects\lups\docker-compose.yaml",
         f"{name}@{ip}:/var/www/docker-compose.yaml"),

        (r"C:\Users\erik\WebstormProjects\lups\lups\dist\lups\*",
          f"{name}@{ip}:/var/www/html/"),

        # (r"C:\Users\erik\PycharmProjects\lups\nginx\nginx.conf",
        #  f"{name}@{ip}:/etc/nginx/nginx.conf"),
    ]

    for s, e in commands:
        print(s, e)
        subprocess.run(["scp", "-i", key, "-r", s, e])

    print("done")


if __name__ == '__main__':
    main()
