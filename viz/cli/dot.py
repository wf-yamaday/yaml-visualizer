import subprocess


def can_use_graphviz():
    can_use = True
    devnull = open('/dev/null', 'w')
    try:
        subprocess.run(['which', 'dot', ], stdout=devnull,
                       shell=False, check=True)
    except subprocess.CalledProcessError:
        can_use = False
    return can_use
