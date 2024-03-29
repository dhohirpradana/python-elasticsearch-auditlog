import os
import uuid
from elasticsearch import Elasticsearch

elastic_url = os.environ.get('ELASTIC_URL')


def handler(data):
    index_name = "sapujagadv2_auditlog"
    uuid4 = uuid.uuid4()
    document_id = uuid4

    print("DATA", data)

    try:
        es = Elasticsearch(hosts=elastic_url)
        es.index(index=index_name, document=data, id=document_id)
        print("Success insert data to elastic")
    except Exception as e:
        print("Error insert data to elastic")
        print(str(e))

# handler({
#     "id": "1",
#     "name": "test",
#     "status": "running",
#     "lastRun": "2020-09-29T15:00:00.000Z",
#     "nextRun": "2020-09-29T15:00:00.000Z",
#     "cronExpression": "0 0 0 * * *",
#     "type": "notebook",
#     "notebook": "test.ipynb",
#     "notebookParams": {
#         "param1": "value1",
#         "param2": "value2"
#     },
# })
