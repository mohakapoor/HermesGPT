# HermesGPT - Automated Internship Outreach Bot 🚀

HermesGPT is an intelligent automation tool designed to streamline the process of reaching out to recruiters for internship opportunities. It integrates AI-generated personalized cold emails, database management, email verification, and automated sending using Gmail API.

## Features

- 📄 **Resume Parsing**: Loads and processes resume data for personalized email generation.
- 🤖 **AI-Powered Emails**: Uses Gemini AI to generate tailored cold emails.
- 📬 **Automated Email Sending**: Sends emails via Gmail API with attachments.
- ✅ **Email Verification**: Uses SMTP and Maileroo API to validate emails before sending.
- 🗄 **Database Management**: Stores recruiter data in PostgreSQL and tracks outreach progress.
- 🔄 **Batch Processing**: Sends emails in batches with randomized delays to prevent spam detection.

## Setup Instructions

### 1. Clone the Repository

```sh
git clone https://github.com/your-username/HermesGPT.git
cd HermesGPT
```

### 2. Install Dependencies

Make sure you have Python installed, then install the required packages:

```sh
pip install -r requirements.txt
```

### 3. Configure Database

Set up a PostgreSQL database with the following schema:

```sql
CREATE TABLE recruiters (
    email TEXT PRIMARY KEY,
    recruiter_name TEXT,
    company_name TEXT,
    role TEXT,
    contacted BOOLEAN DEFAULT FALSE
);
```

### 4. Set Up Gmail API

1. Enable the Gmail API from Google Cloud Console.
2. Download `credentials.json` and place it in the project directory.
3. Run authentication:

```sh
python main.py
```

### 5. API Keys

- **Gemini AI API**: Add your Gemini API key to the `API_KEY` variable.

### 6. Load Recruiter Data

Prepare a CSV file (`recruiters.csv`) with the following columns:

| Email | Name | Company | Title |
|-------|------|---------|-------|
| example@email.com | John Doe | Google | Hiring Manager |

Then, load it into the database:

```sh
python -c "from main import load_recruiters; load_recruiters('recruiters.csv')"
```

### 7. Run the Outreach Script

```sh
python main.py
```

## How It Works

1. **Resume Loading**: The script reads the resume and stores its details in AI memory.
2. **Recruiter Selection**: Fetches recruiters from the database who haven't been contacted.
3. **Email Verification**: Ensures the email is valid before sending.
4. **AI-Generated Email**: Gemini AI crafts a custom email based on the recruiter's details.
5. **Automated Sending**: Uses Gmail API to send the email with an attached resume.
6. **Logging & Tracking**: Updates the database to mark recruiters as contacted.

## Future Improvements

- 🌍 Multi-language support
- 🔎 Enhanced recruiter filtering
- 📊 Analytics dashboard for tracking response rates

## Contributing

Feel free to fork this project and submit pull requests! 🚀

## License

This project is open-source under the [MIT License](LICENSE).
