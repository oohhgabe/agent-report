# <img src="./static/logo3.png" width="50px" style="transform: translateY(20%); padding-right: 10px">**Agent Report Application**

# Getting started

## **Install python**

If you have Python installed in your computer, you can skip this section. To check if you have Python installed, go to Powershell if you're on Windows or Terminal if you're on MacOS.

### **For Windows, type the following command in PowerShell and press Enter:**

`python --version`

If you don't have a version of Python on your system, then the above command will launch the MS Store and redirect you to the Python application page.

### **For MacOS, type the following command in Terminal and press Return:**

`python3 --version`

If this command did not return a version number, then you must install Python.

### **For Windows users, Python can be installed from the following:**

- MS Store: Can be accessed from the command above
- Python.org: Can be accessed [here](https://www.python.org/downloads/windows/)

### **For MacOS users, Python can be installed from the following:**

- Python.org: Can be accessed [here](https://www.python.org/downloads/macos/)
- Homebrew: [Install Homebrew](https://brew.sh) if you haven't already and follow the steps

If any issues arise during your installation process, you can find a helpful guide [here](https://realpython.com/installing-python/)

## **Download the project**

Around the top there is a big green button with the word "<> Code" on it. Click it and select the last option **Download Zip**

Next, extract the zip file and store it in a new folder in an accessible location. Once the project folder is stored in a location of your liking, copy its absolute path.

### **Open the Terminal or PowerShell and write the following command:**

`cd <your-absolute-path-goes-here>`

Then, press Enter. To successfully check if you're in the absolute path you should see the name of the project folder in the Command Line Interface. Furthermore, if you type `ls` you should see various files, such as wwi and invoice.

## **Create a Python Virtual Environment**

Now that we are inside the project folder, we need to create a virtual environment to be able to run the app.

### **On Windows, type the following inside the PowerShell that you used in the previous section:**

`python -m venv venv`

### **On MacOS, type the following inside the Terminal that you used in the previous section:**

`python3 -m venv venv`

## **Now, activate the virtual environment**

Note, before activating the virtual environment, make sure that you're inside the folder where you created the virtual environment.

### **On Windows, type the following inside the PowerShell:**

`venv\Scripts\activate`

### **On MacOS, type the following inside the Terminal:**

`source venv/bin/activate`

If you successfully activated your virtual environment, you should see the name of it in your command line interface.

In addition, to deactivate your virtual environment, simply type `deactivate` in the command line.

## **Install the required packages**

Inside the project folder with an active virtual environment, type the following in your command line interface:

`pip install -r requirements.txt`

## **Run the Agent Report App**

With everything successfully installing inside your virtual environment, type the following commands in order:

1. `python manage.py makemigrations`
2. `python manage.py migrate`
3. `python manage.py createsuperuser`

Create an account with the credentials of your liking, and lastly type:

`python manage.py runserver`

Note, for Windows users, instead of typing `python`, simply type `py`.

**If everything was successful, a link will be provided in the terminal. Simply copy and paste in your browser and login with your credentials**
