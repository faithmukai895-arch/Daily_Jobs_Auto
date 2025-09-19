from googleapiclient.discovery import build
import pickle
import os
from google.auth.transport.requests import Request
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import re
import time
import base64  # For GitHub Actions token decoding
from google.colab import drive  # For Colab Drive mount (optional)

# Mount Drive for persistence (Colab-specific)
try:
    drive.mount('/content/drive')
except:
    pass  # Ignore if not in Colab (e.g., GitHub Actions)

# Your Blog ID
BLOG_ID = '71655510733035331'

def authenticate():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("Token expired or missing. Re-authentication needed!")
            return None
    # Save credentials to Drive (Colab) or local (GitHub Actions)
    if os.path.exists('/content/drive'):
        with open('/content/drive/MyDrive/token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('blogger', 'v3', credentials=creds)

def fetch_myjobmag_jobs(limit=40):
    jobs = []
    url = 'https://www.myjobmag.co.ke/jobs'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'}
    response = requests.get(url, headers=headers)
    print(f"MyJobMag Response Status: {response.status_code}")
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        job_cards = soup.find_all('div', class_=re.compile(r'job|listing|item', re.I), limit=limit * 3)
        for card in job_cards:
            title_elem = card.find(['h3', 'h2', 'a', 'span'], class_=re.compile(r'title|job', re.I))
            title = title_elem.text.strip() if title_elem else ''
            if title and len(title) > 10:
                link_elem = card.find('a', href=True)
                link = 'https://www.myjobmag.co.ke' + link_elem['href'] if link_elem and not link_elem['href'].startswith('http') else link_elem['href'] if link_elem else url
                desc_elem = card.find(['p', 'div'], class_=re.compile(r'desc|summary', re.I))
                desc = desc_elem.text.strip()[:500] + '...' if desc_elem else 'Exciting Kenyan opportunity. Apply for full details.'
                company_elem = card.find(['span', 'div'], class_=re.compile(r'company|employer', re.I))
                company = company_elem.text.strip() if company_elem else 'MyJobMag Partner'
                location_elem = card.find(['span', 'div'], class_=re.compile(r'location|place', re.I))
                location = location_elem.text.strip() if location_elem else 'Nairobi, Kenya'
                jobs.append({
                    'title': title,
                    'url': link,
                    'description': desc,
                    'company': company,
                    'location': location,
                    'published': str(datetime.now())
                })
    time.sleep(2)  # Polite delay
    return jobs[:limit]

def fetch_improved_jobs(limit=40):
    jobs = fetch_myjobmag_jobs(limit)
    if len(jobs) < limit:
        fallback = [
            {
                'title': 'Finance Manager - MyJobMag Sample',
                'url': 'https://www.myjobmag.co.ke/job/finance-manager-nairobi',
                'description': 'Lead financial operations for a growing Kenyan firm...',
                'company': 'Sample Corp',
                'location': 'Nairobi, Kenya',
                'published': str(datetime.now())
            }
        ]
        jobs += fallback[:limit - len(jobs)]
    print(f"Fetched {len(jobs)} jobs from MyJobMag.")
    return jobs

def format_job_post(job):
    title = job['title']
    company = job['company']
    location = job['location']
    description = job['description']
    published = job['published']
    salary = 'KSh 80,000 - 120,000' if 'Finance' in title else 'Negotiable'
    deadline = (datetime.strptime(published, '%Y-%m-%d %H:%M:%S.%f') + timedelta(days=30)).strftime('%d %B %Y')

    # Tailored duties (10-15 items based on title keywords)
    if any(word in title.lower() for word in ['finance', 'officer', 'compliance', 'manager']):
        duties = [
            'Conduct thorough audits of financial records to ensure accuracy and compliance.',
            'Develop and implement internal control policies to mitigate organizational risks.',
            'Monitor adherence to Kenyan legal and regulatory requirements.',
            'Prepare detailed reports on compliance status for senior management review.',
            'Collaborate with project teams to align controls with business goals.',
            'Train staff on compliance protocols and ethical business practices.',
            'Investigate discrepancies or potential fraud within the organization.',
            'Liaise with external auditors during annual financial reviews.',
            'Update compliance documentation in line with evolving regulations.',
            'Assess the effectiveness of existing control measures regularly.',
            'Provide guidance on policy interpretation to departmental heads.',
            'Ensure timely resolution of all compliance-related issues.',
            'Support the development of comprehensive risk management strategies.',
            'Maintain strict confidentiality of sensitive financial data.'
        ]
    else:
        duties = [
            'Design and align technology solutions with core business needs.',
            'Develop integrated views of enterprise architecture for scalability.',
            'Collaborate with stakeholders to define and refine IT strategies.',
            'Evaluate and recommend emerging technologies for adoption.',
            'Oversee the implementation of architectural frameworks and standards.',
            'Ensure system scalability and optimal performance across operations.',
            'Conduct risk assessments on all proposed IT projects.',
            'Provide technical guidance and support to development teams.',
            'Maintain up-to-date documentation of architectural designs.',
            'Liaise with vendors for seamless technology solutions integration.',
            'Monitor industry trends to inform proactive strategy adjustments.',
            'Support digital transformation initiatives within the organization.',
            'Ensure full compliance with IT governance and security standards.'
        ]

    # Tailored qualifications (5-10 items)
    if any(word in title.lower() for word in ['finance', 'officer', 'compliance', 'manager']):
        quals = [
            'Bachelor’s degree in Finance, Accounting, or a related field.',
            'Minimum of 3 years’ experience in compliance or internal auditing.',
            'Professional certification in risk management or internal auditing (e.g., CIA, CRMA).',
            'Strong analytical skills with keen attention to detail.',
            'Proficiency in financial software and Microsoft Office Suite.',
            'Knowledge of Kenyan financial regulations and standards.',
            'Excellent communication and interpersonal skills.',
            'Ability to work independently in high-pressure environments.',
            'Experience in a development or NGO setting is highly advantageous.'
        ]
    else:
        quals = [
            'Bachelor’s degree in Computer Science, IT, or equivalent.',
            'At least 5 years’ experience in enterprise architecture or IT.',
            'Familiarity with IT governance frameworks (e.g., TOGAF, Zachman).',
            'Strong problem-solving and technical aptitude.',
            'Hands-on experience with cloud computing platforms (e.g., AWS, Azure).',
            'Excellent project management and stakeholder collaboration skills.',
            'Ability to translate complex technical concepts to business language.',
            'Proven track record in digital transformation projects.'
        ]

    # SEO Enhancements
    meta_keywords = 'jobs in Kenya, Nairobi jobs, ' + ', '.join([word for word in [title, company, location.split(',')[0], 'employment', 'careers'] if word])
    meta_description = f"Explore the {title} role at {company} in {location}. Apply by {deadline} for a salary of {salary}. Join Kenya's leading job opportunities!"

    content = f"""
    <h1>Job Vacancies at <b>{company}</b> – Apply Now!</h1>
    <!-- Meta Data -->
    <meta name="keywords" content="{meta_keywords}">
    <meta name="description" content="{meta_description}">
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org/",
        "@type": "JobPosting",
        "title": "{title}",
        "description": "{description}",
        "identifier": {{
            "@type": "PropertyValue",
            "name": "{company}",
            "value": "JobID-{hash(str(job))}"
        }},
        "datePosted": "{published}",
        "validThrough": "{datetime.strptime(deadline, '%d %B %Y').isoformat()}",
        "employmentType": "FULL_TIME",
        "hiringOrganization": {{
            "@type": "Organization",
            "name": "{company}",
            "sameAs": "{job['url']}"
        }},
        "jobLocation": {{
            "@type": "Place",
            "address": {{
                "@type": "PostalAddress",
                "addressLocality": "{location.split(',')[0]}",
                "addressRegion": "Kenya",
                "addressCountry": "KE"
            }}
        }},
        "baseSalary": {{
            "@type": "MonetaryAmount",
            "currency": "KES",
            "value": {{
                "@type": "QuantitativeValue",
                "minValue": {salary.split('-')[0].replace('KSh ', '')},
                "maxValue": {salary.split('-')[1].replace('KSh ', '') if '-' in salary else salary.replace('KSh ', '')},
                "unitText": "MONTH"
            }}
        }}
    }}
    </script>

    <h2>Introduction</h2>
    <p>{company}, a renowned organization in the {'development and cooperation' if any(w in company.lower() for w in ['giz', 'ngo']) else 'business and finance'} sector, is expanding its operations in Kenya with a focus on sustainable growth and innovation. Established over decades ago, it has built a strong reputation for delivering impactful projects in areas like {'healthcare, education, and economic development' if any(w in company.lower() for w in ['giz', 'ngo']) else 'financial services and technology'}. Operating primarily from its <i>{location.split(',')[0]}</i> office, {company} collaborates with local and global partners to address key challenges in the region.</p>
    <p>This recruitment drive offers a chance to join a dynamic team committed to excellence and community impact. With a mission to foster inclusive {'development and cooperation' if any(w in company.lower() for w in ['giz', 'ngo']) else 'financial inclusion and innovation'}, {company} is seeking talented individuals to contribute to its initiatives across Kenya.</p>

    <h2>{title}</h2>
    <h3>Job Overview</h3>
    <ul>
        <li><b>Location</b>: {location}</li>
        <li><b>Positions Available</b>: 1</li>
        <li><b>Employment Type</b>: Permanent</li>
        <li><b>Deadline</b>: {deadline}</li>
        <li><b>💰 Salary</b>: {salary}</li>
    </ul>

    <h3>Job Summary</h3>
    <p>{company} is seeking a dedicated <b>{title}</b> to ensure robust oversight and innovation in {location}. This role involves critical responsibilities in {'compliance and risk management' if any(w in title.lower() for w in ['finance', 'officer', 'compliance']) else 'enterprise architecture and IT strategy'}, supporting key projects with precision. Join a team driving impactful change in Kenya's {'development landscape' if any(w in title.lower() for w in ['finance', 'officer', 'compliance']) else 'financial technology sector'}.</p>

    <h3>Duties & Responsibilities</h3>
    <ul>
        {''.join([f'<li>{duty}</li>' for duty in duties])}
    </ul>

    <!---WhatsApp Channel Banner--->
    <div class="separator" style="clear: both; text-align: center;"><a href="https://whatsapp.com/channel/0029Vag7DgaFcovxpkZuUG25" rel="nofollow" style="margin-left: 1em; margin-right: 1em;" target="_blank"><img alt="Daily Jobs WhatsApp Channel Banner" border="0" data-original-height="250" data-original-width="970" height="136" src="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiXW9123n3DTa6lBy494oroKMY6evH8b4iAAF8QFPlPk-93UMoGnfRHx6KikL01qejkaj_hqRLmV3PRxQpRvfAiGv5OJghyphenhyphenk58LkstDKHw7jmE4mjOI2iqZmjHJpIb2bTcxruzLiAOZhw6cJpro-qhSYxRMpcU28bEOwuocjMdptrGqXRtOUYZgObSg9r0/w619-h136/join-whatsapp-channel%20Image.webp" title="Daily Jobs WhatsApp Channel Banner" width="619" /></a></div>
    <!---End of Whatsapp Channel Banner--->

    <h3>Qualifications & Requirements</h3>
    <ul>
        {''.join([f'<li>{qual}</li>' for qual in quals])}
    </ul>

    <h3>How to Apply</h3>
    <p>Interested candidates should submit their <b>CV</b>, <b>cover letter</b>, and copies of certifications to <b>hr@{company.lower().replace(' ', '')}.org</b> by {deadline}. Ensure all documents are in PDF format and include <i>{title} Application</i> in the subject line.</p>

    <!---COVER LETTER GENERATOR BUTTON STARTS HERE--->
    <div class="bg-green-100 border-l-4 border-green-500 p-4 mb-6 rounded-lg text-center"><p class="font-semibold text-lg text-gray-800" style="text-align: center;"><span style="text-align: left;">🔹</span><b><span style="color: #38761d;">Create a Winning Cover Letter in</span><span style="color: #3d85c6;"> 1 Minute!</span><span style="color: #38761d;"> Pay Ksh 36 to Download Now!</span></b><span style="text-align: left;">🔹</span></p></div>
    <div style="align-items: center; display: flex; flex-direction: column; justify-content: center; margin: 20px 0px; text-align: center;">
        <a href="https://thecvarchitect.github.io/Aibuilder/index.html" rel="nofollow" style="text-decoration: none;" target="_blank">
            <button onmouseout="this.style.backgroundColor='#007BFF'; this.style.transform='translateY(0)'; this.style.boxShadow='0px 4px 6px rgba(0, 0, 0, 0.1)';" onmouseover="this.style.backgroundColor='#0056b3'; this.style.transform='translateY(-2px)'; this.style.boxShadow='0px 6px 12px rgba(0, 0, 0, 0.2)';" style="background-color: #007bff; border-radius: 8px; border: none; box-shadow: rgba(0, 0, 0, 0.1) 0px 4px 6px; color: white; cursor: pointer; font-size: 16px; font-weight: bold; padding: 12px 24px; transition: 0.3s ease-in-out;">
              Generate Your Application Letter</button></a></div>
    <!---COVER LETTER GENERATOR BUTTON ENDS HERE--->

    <!--ADDONS 01-->

    <!--APPLY NOW BUTTON-->

    <div style="align-items: center; display: flex; flex-direction: column; justify-content: center; margin: 20px 0px; text-align: center;">
        <a href="https://www.dailyjobs.co.ke/" rel="" style="text-decoration: none;" target="_blank"><button onmouseout="this.style.backgroundColor='#007BFF'; this.style.transform='translateY(0)'; this.style.boxShadow='0px 4px 6px rgba(0, 0, 0, 0.1)';" onmouseover="this.style.backgroundColor='#0056b3'; this.style.transform='translateY(-2px)'; this.style.boxShadow='0px 6px 12px rgba(0, 0, 0, 0.2)';" style="background-color: #007bff; border-radius: 8px; border: none; box-shadow: rgba(0, 0, 0, 0.1) 0px 4px 6px; color: white; cursor: pointer; font-size: 16px; font-weight: bold; padding: 12px 24px; transition: 0.3s ease-in-out;">MORE JOBS</button></a>
        <p style="font-size: 14px; font-style: italic; margin-top: 10px;"><b><span style="color: #38761d;">Join Our WhatsApp Group For More Jobs</span></b></p>
    </div>
    <!--ADDONS 02-->
    <!--WhatsApp Group and Channel Box-->
    <div style="background: linear-gradient(135deg, rgb(255, 255, 255), rgb(236, 229, 221)); border-radius: 10px; box-shadow: rgba(0, 0, 0, 0.1) 4px 4px 15px; margin: 20px auto; max-width: 700px; padding: 20px; text-align: center;">
      <h2 onclick="document.getElementById('whatsappList').classList.toggle('collapsed');" style="color: #075e54; cursor: pointer; font-size: 20px; margin-bottom: 15px;">
        <img src="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjyKz4Yu9viLm_EQoNk1zLMNjTYAkSw6HWd-wd5CVylk0cN1TtSOYjXrpSvURsb7S2fuXYGyQb_J7SzxkO-pqgtXqY1AVAuaLTShBxCZRGUSeehK9-YS25_QRPoAHIV4zJqxIlxVT9ZvMYkS0QThnx8rDo5Ffz7giHBacpVgczVfy9dR9UD56PrgCo0nUk/s64/WhatsApp%20favicon-64x64.webp" style="margin-right: 8px; vertical-align: middle; width: 24px;" />WhatsApp Groups
      </h2>
      <div id="whatsappList" style="max-height: 500px; overflow: hidden; transition: max-height 0.5s;">
        <div style="align-items: center; background: rgb(255, 255, 255); border-radius: 8px; display: flex; margin: 10px 0px; padding: 10px;">
          <a href="https://chat.whatsapp.com/HjasGgKnkBZ4S64L1Y55b1" style="color: #2d3748; font-size: 16px; font-weight: 500; text-decoration: none;">Daily Jobs - Group 5 (full)</a></div>
        <div style="align-items: center; background: rgb(255, 255, 255); border-radius: 8px; display: flex; margin: 10px 0px; padding: 10px;">
          <a href="https://chat.whatsapp.com/ECO6GcHVfok9lizoJrcAnw" style="color: #2d3748; font-size: 16px; font-weight: 500; text-decoration: none;">Daily Jobs - Group 6</a>
        </div>
        <div style="align-items: center; background: rgb(255, 255, 255); border-radius: 8px; display: flex; margin: 10px 0px; padding: 10px;">
          <a href="https://chat.whatsapp.com/CwXARl276ys2i1R3b7Cs6G" style="color: #2d3748; font-size: 16px; font-weight: 500; text-decoration: none;">Daily Jobs - Healthcare</a>
        </div>
        <div style="align-items: center; background: rgb(255, 255, 255); border-radius: 8px; display: flex; margin: 10px 0px; padding: 10px;">
          <a href="https://chat.whatsapp.com/B6yoqepmRgD4ibpwW3kCpk" style="color: #2d3748; font-size: 16px; font-weight: 500; text-decoration: none;">Daily Jobs - Business 3</a>
        </div>
        <div style="align-items: center; background: rgb(255, 255, 255); border-radius: 8px; display: flex; margin: 10px 0px; padding: 10px;">
          <a href="https://chat.whatsapp.com/G2lOCv6HU5PF1vlvlu3h9R" style="color: #2d3748; font-size: 16px; font-weight: 500; text-decoration: none;">Daily Jobs - Remote 2</a>
        </div>
        <div style="align-items: center; background: rgb(255, 255, 255); border-radius: 8px; display: flex; margin: 10px 0px; padding: 10px;">
          <a href="https://whatsapp.com/channel/0029Vag7DgaFcovxpkZuUG25" style="color: #2d3748; font-size: 16px; font-weight: 500; text-decoration: none;">Daily Jobs - WhatsApp Channel 2</a>
        </div>
      </div>
    </div>
    <!--ADDONS 03-->
    <!--Safety Tips Box-->
    <div style="background-color: #fff3cd; border-radius: 10px; box-shadow: rgba(0, 0, 0, 0.15) 4px 4px 15px; margin-top: 20px; padding: 20px; text-align: left;">
      <h2 style="color: #856404; font-size: 18px; text-align: left;">Safety Tips</h2>
      Be cautious of job offers that require upfront payments.<br />Verify the authenticity of the company before sharing personal information.<br />Report suspicious job postings to the appropriate authorities.<ul style="list-style-type: none; padding-left: 0px;">
      </ul>
    </div>

    <h2>Call-to-Action</h2>
    <p>Don’t miss out on this exciting opportunity with <b>{company}</b>! Apply today before the deadline of {deadline} and take the first step toward a rewarding career.</p>
    """
    return content

def publish_job_post(service, blog_id, job):
    body = {
        'kind': 'blogger#post',
        'blog': {'id': blog_id},
        'title': f'Job Vacancies at {job["company"]} – Apply Now!',
        'content': format_job_post(job)
    }
    try:
        request = service.posts().insert(blogId=blog_id, body=body)
        response = request.execute()
        print(f"Posted: {response['title']} - Check at {response['url']}")
        return response
    except Exception as e:
        print(f"Failed to post {job['title']}: {e}")
        return None

def run_daily_job_posting():
    service = authenticate()
    if not service:
        print("Authentication failed. Re-run authentication cell!")
        return
    
    # Handle GitHub Actions environment variables for credentials
    if 'GOOGLE_CREDENTIALS' in os.environ and 'TOKEN_PICKLE' in os.environ:
        with open('credentials.json', 'w') as f:
            f.write(os.environ['GOOGLE_CREDENTIALS'])
        with open('token.pickle', 'wb') as f:
            f.write(base64.b64decode(os.environ['TOKEN_PICKLE']))

    jobs = fetch_improved_jobs(40)  # Target 40 jobs
    for job in jobs:
        publish_job_post(service, BLOG_ID, job)

    # Simulate next run (for testing; GitHub Actions handles scheduling)
    next_run = datetime.now() + timedelta(days=1)
    print(f"Next run scheduled for: {next_run.strftime('%Y-%m-%d %H:%M:%S')} EAT")
    print("Note: Automated via GitHub Actions at 8:00 AM EAT.")

if __name__ == "__main__":
    run_daily_job_posting()
