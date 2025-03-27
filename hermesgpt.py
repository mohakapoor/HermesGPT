import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import time,random
import google.generativeai as genai
import pathlib
import os
import psycopg2
import pandas as pd
import smtplib



API_KEY = "YOUR_GEMINI_API_KEY"
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def connect_db():
    return psycopg2.connect(
            dbname = "hermesgpt",
            user = "postgres",
            password = "1234",
            host = "localhost",
            port = "5432",
        )

def load_recruiters(csv_path):
    try:
        recruiters = pd.read_csv(csv_path)
        conn = connect_db()
        cursor = conn.cursor()
        query = """
        INSERT INTO recruiters (email,recruiter_name,company_name,role)
        VALUES (%s,%s,%s,%s) 
        ON CONFLICT (email) DO NOTHING;
        """
        for idx,row in recruiters.iterrows():
            cursor.execute(query,(row["Email"],row['Name'],row['Company'],row['Title']))
            print(f"Row {idx} with name {row['Name']} executed properly")
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Eror occured {e}")
    finally:
        cursor.close()
        conn.close()

def get_recruiters(batch_size=40):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = """
        SELECT email,recruiter_name,company_name, role FROM recruiters WHERE contacted = FALSE LIMIT %s;
        """
        cursor.execute(query,(batch_size,))

        recruiters = cursor.fetchall()
        
    except Exception as e:
        print(f"Error {e} occurred")
    finally:
        cursor.close()
        conn.close()

        return recruiters

def mark_as_contacted(email):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = """
        UPDATE  recruiters SET contacted = TRUE WHERE email = %s;
        """
        cursor.execute(query,(email,))
        conn.commit()
    except Exception as e:
        print(f"Eror {e} occurred")
    finally:
        cursor.close()
        conn.close()

genai.configure(api_key=API_KEY)
chat = genai.GenerativeModel('gemini-2.0-flash').start_chat(history=[])

def load_resume(resume_path):

    try:
        if not os.path.exists(resume_path):
            print(f"Error: file not found at {resume_path}")
        
        resume_details = pathlib.Path(resume_path).read_bytes()
        if not resume_details:
            print("Error: This if file is empty")
            return None
        
        print(f'Resume loaded successfully ({len(resume_details)} bytes)')
        return resume_details

    except Exception as e:
        print(f"Error {e} has occurred")
        return None




def model_loading(resume_path):
    resume_details = load_resume(resume_path)
    if resume_path != None:
        prompt = "Load this resume in your memory. I will later ask you to generate me cold emails based on the details I will provide you Later. Also this is the link to my github = https://github.com/mohakapoor . Go through it as well and no need to add the link to the body."
        response = chat.send_message(
            content=[
                {"mime_type": "application/pdf", "data": resume_details},
                prompt
            ]
        )
        print(response.text)
    else:
        print("Couldn't load the model")

def initial_outreach(user,company,recruiter_name,title="HR Manager"):
    response = chat.send_message(
        content=[
            f"""
            Generate a professional cold email to {recruiter_name}, with the title {title} at {company}, inquiring about internship opportunities for the (fill this according to my resume and company) position based on the resume details provided to you earlier.
            Make sure it is custom tailored to me.

            1.Start with a concise introduction about myself, including key skills and relevant experience.
            2.Express genuine interest in the company and why I want to intern there.
            3.Briefly mention a key project or achievement that aligns with the role.
            4.End with a polite call to action, asking about internship openings or guidance on applying.
            5.Keep the email professional, friendly, and under 200 words.
            6.Make sure there are no placeholders in the text
            You could include a small text in the end like : "P.S Im mailing this through a automated internship applying bot made by me" do it a bit creatively
            Make sure you only return the mail body & subject nothing else.
            """
        ]
    )
    
    
    str = response.text
    str = str.split('\n',1)
    subject,body = str[0],str[1]
    print(subject)
    print(body)

    return subject,body
def authenticate_gmail(user):
    creds = None
    token_path = f"token_{user}.json"
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            return creds
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(token_path, "w") as token:
            token.write(creds.to_json())
    
    return creds


def send_email(user,recipient, subject, message_text,attachment_path=None):
    creds = authenticate_gmail(user)
    service = build("gmail", "v1", credentials=creds)
    
    message = MIMEMultipart()
    message["to"] = recipient
    message["subject"] = subject
    message.attach(MIMEText(message_text,"plain"))

    if attachment_path:
        part = MIMEBase("application", "octet-stream")
        with open(attachment_path, "rb") as attachment:
            part.set_payload(attachment.read())

        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f'attachment; filename="{os.path.basename(attachment_path)}"',
        )
        message.attach(part)


    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    send_message = {"raw": raw_message}
    service.users().messages().send(userId="me", body=send_message).execute()
    print(f" Email sent to {recipient}")


def smtp_verify_email(email):
    domain = email.split('@')[-1]

    try:
        mx_record = smtplib.SMTP(f"mx.{domain}", 25, timeout=5)
        mx_record.quit()
        print(f"{email} is deliverable.")
        return True
    except Exception:
        print(f"{email} is undeliverable.")
        return False
    

def batch_mailing(user,batch_size=40):
    recruiters = get_recruiters()
    count = 1
    for recruiter in recruiters:
        email,recruiter_name,company_name,title = recruiter
        if smtp_verify_email(email):
            subject,body = initial_outreach(user,company_name,recruiter_name,title)

            send_email(user,email,subject,body,"Resume.pdf")
            
            mark_as_contacted(email)
            
            print(f"{count/50*100}% emails sent")
            count+=1
            time.sleep(random.randint(30,120))
        else:
            continue

model_loading("Resume.pdf")

batch_mailing("Mohak")