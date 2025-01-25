import subprocess


def start_npm():
    subprocess.run('npm start', cwd="frontend", shell=True)
