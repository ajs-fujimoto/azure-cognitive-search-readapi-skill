import logging
import re
import time

'''
Read and extract from the image
'''
def read_text(client, stream):
    # Read API using binary stream
    # Read supports auto language identification and multi-language documents
    response = client.read_in_stream(stream, raw=True)
    
    # Get ID from returned headers
    operation_location = response.headers["Operation-Location"]
    operation_id = operation_location.split("/")[-1]
    logging.info(f'CogSvc operation_id: {operation_id}')
    # SDK call that gets what is read
    while True:
        result = client.get_read_result(operation_id)
        if result.status not in ['notStarted', 'running']:
            break
        logging.info('Waiting for result...')
        #Polling for operations
        time.sleep(10)
    return result

'''
To fix the Japanese character separation problem.
Remove half-width spaces after double-byte characters.
'''
def remove_spaces(text):
    pattern1 = re.compile(r"([^\x01-\x7E])\x20")
    removed_text = pattern1.sub(r"\1", text)
    return removed_text

