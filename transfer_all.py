import subprocess
import os


# (r"C:\Users\erik\WebstormProjects\lups\lups\dist\lups\*",
#  f"{name}@{ip}:/var/www/html"),

def main():
    key = r"C:\Users\erik\.ssh\digital"
    ip = "165.232.82.30"
    name = "erik"

    # todo add current dir not lups1 or lups2

    commands = [

        # (r"C:\Users\erik\PycharmProjects\lups2\data",
        #  f"{name}@{ip}:/var/www/data"),
        #
        (r"C:\Users\erik\PycharmProjects\lups\celeryr\t5-model",
         f"{name}@{ip}:/home/erik/lups/celeryr"),
        #
        # (r"C:\Users\erik\PycharmProjects\lups2\flaskr",
        #  f"{name}@{ip}:/var/www/"),
        #
        # (r"C:\Users\erik\PycharmProjects\lups2\docker-compose.yaml",
        #  f"{name}@{ip}:/var/www/docker-compose.yaml"),
        #
        # (r"C:\Users\erik\WebstormProjects\lups3\lups\dist\lups\*",
        #   f"{name}@{ip}:/var/www/html/"),
        #
        # (r"C:\Users\erik\PycharmProjects\lups2\nginx\nginx.conf",
        #  f"{name}@{ip}:/etc/nginx/nginx.conf"),
    ]

    for s, e in commands:
        print(s, e)
        subprocess.run(["scp", "-i", key, "-r", s, e])

    print("done")


if __name__ == '__main__':
    main()
