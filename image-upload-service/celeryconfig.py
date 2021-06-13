broker_url = 'redis://'
result_backend = 'redis://'

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
enable_utc = True
imports = ["server.api.tasks"]
