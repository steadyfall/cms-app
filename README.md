# Content Management System


### Setup

1. Clone this repo to your own local machine with this command: \
`git clone https://github.com/steadyfall/cms-app.git`

2. We recommend you that you clone this repo to a working directory with a virtual environment. You can create and activate the virtual environment by the following command: 
> - Bash: `python3 -m venv venv; source ./venv/bin/activate;`
> - Powershell: `py -m venv venv; .\venv\Scripts\Activate.ps1;`

3. After cloning the repo, install the required libraries via the requirements.txt file with this command:
> - Bash: `python3 -m pip install -r requirements.txt`
> - Powershell: `pip install -r requirements.txt`

4. After installing the required libraries, migrate all changes to the database by running:
> - Bash: `python3 manage.py makemigrations; python3 manage.py migrate;`
> - Powershell: `py manage.py makemigrations; py manage.py migrate;`

5. After migrating to the database, you can create an admin user with following command:
> - Bash: `python3 manage.py createsuperuser`
> - Powershell: `py manage.py createsuperuser`

\
\
Now you can successfully test the CMS by running it on the local machine at ![localhost:8008](http://127.0.0.1:8008/) via this comamnd:
> - Bash: `python3 manage.py runserver 8008`
> - Powershell: `py manage.py runserver 8008`

\
Login using the **user credentials you made** in Step 5 and Bravo, you can now ***ACCESS the CMS and its Admin Panel!***


