import datetime
import requests
import logging
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

#Key Vault setup
KEY_VAULT_NAME = "Lab4-KeyV" 
KV_URI = f"https://{KEY_VAULT_NAME}.vault.azure.net"
credential = DefaultAzureCredential()
kv_client = SecretClient(vault_url=KV_URI, credential=credential)

SENDGRID_API_KEY = kv_client.get_secret("sendgrid-api-key").value

# Task API Endpoint
TASK_API_URL = "https://lab4-api-management.azure-api.net/tasks"  

def send_email_notification(task):
    """Send notification via SendGrid API (or other service)."""
    import sendgrid
    from sendgrid.helpers.mail import Mail

    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    message = Mail(
        from_email='noreply@taskmanager.com',
        to_emails='cody.tran@edu.sait.ca',  # Replace with user's email
        subject=f"Task Due Soon: {task['title']}",
        plain_text_content=f"Reminder: Task '{task['title']}' is due on {task['due_date']}"
    )
    response = sg.send(message)
    logging.info(f"Sent notification for task {task['id']}, status {response.status_code}")

def main(mytimer: func.TimerRequest) -> None:
    logging.info('Timer trigger function started.')

    try:
        response = requests.get(TASK_API_URL)
        tasks = response.json()
    except Exception as e:
        logging.error(f"Error fetching tasks: {e}")
        return

    now = datetime.datetime.utcnow()
    for task in tasks:
        if 'due_date' in task:
            due_date = datetime.datetime.fromisoformat(task['due_date'].replace("Z", "+00:00"))
            if 0 <= (due_date - now).total_seconds() <= 86400:
                send_email_notification(task)

    logging.info('Timer trigger function finished.')
