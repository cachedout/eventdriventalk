import docker
'''
Some silly Docker examples
'''
def container_exists(container):
    d = docker.Client()
    return container in d.containers()
