import datetime
import io
import json 
import logging
import pprint
from reportlab.platypus import SimpleDocTemplate, Paragraph, Preformatted
from reportlab.lib.styles import getSampleStyleSheet

logger = logging.getLogger(__name__)


def list_drive_items(user_client):
    request_url = 'https://graph.microsoft.com/v1.0/me/drive/root/children'
    response = user_client.get(request_url)
    for item in response.json()['value']:
        logger.warning(f"{item['id']=} {item['name']=}")
    return response


def create_folder_in_onedrive(user_client):
    request_url = 'https://graph.microsoft.com/v1.0/me/drive/root/children'
    request_body = {
        "name": "Kantara_Reports",
        "folder": {},
        "@microsof.conflictBehavior": "rename"
    }
    response = user_client.post(request_url,
                                data=json.dumps(request_body),
                                headers={'Content-Type':'application/json'})
    
    logger.warning(f"response= \n{pprint.pformat(response.json())}")
    return response 

document_id = None


def fetch_documents_id(user_client):
    global document_id
    if document_id is None:
        request_url = 'https://graph.microsoft.com/v1.0/me/drive/root/children'
        response = user_client.get(request_url)
        for item in response.json()['value']:
            logger.warning(f"{item['id']= } {item['name']= }")
            if item['name'] == "Kantara_Reports":
                document_id = item['id']
                break

    logger.warning(f"{document_id}")
    return document_id


def upload_file_on_one_drive(user_client):
    with open("myTest.txt",'w') as file:
        file.write("Hello World")
    # filename = "myTest.txt"
    with io.BytesIO() as pdf_buffer:
        doc = SimpleDocTemplate(pdf_buffer)
        story = [
            Paragraph(datetime.datetime.now().strftime('%Y-%m-%D %H:%M:%S')),
            Preformatted("sample", getSampleStyleSheet()['Code'])
        ]
        doc.build(story)
        bytes_pdf = pdf_buffer.getvalue()
        
    filename = "mypdf.pdf"    
    request_url = f"https://graph.microsoft.com/v1.0/me/drive/items/{fetch_documents_id(user_client)}:/{filename}:/content"
    response = user_client.put(request_url,
                               data= bytes_pdf,
                               headers={'Content-type':'application/json'})
    logger.warning(f"response = \n{pprint.pformat(response.json())}")
    return response
