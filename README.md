# matcha2.0
PDF Comparison Tool with GUI this is an experimental python program

Anaconda Installation and Running a Python Script

1. Install Anaconda:
   - Go to https://www.anaconda.com/download and download the installer for your operating system.
   - Run the installer and follow the on-screen instructions. It's generally recommended to accept the default settings unless you have a specific reason to change them.

2. Open Anaconda Prompt:
   - After the installation is complete, open the Anaconda Prompt. You can usually find it by searching in your Start Menu (Windows) or in your Applications folder (macOS/Linux).

3. Create a New Virtual Environment:
   - In the Anaconda Prompt, type the following command and press Enter:
     ```
     conda create -n env_name python=3.9 -y
     ```
     - **Explanation:**
       - `conda create`: This is the command to create a new conda environment.
       - `-n env_name`: This specifies the name you want to give to your new environment. Replace `env_name` with your desired name (e.g., `matcha_env`).
       - `python=3.9`: This specifies the Python version you want to use in this environment. You can change `3.9` to a different version if needed.
       - `-y`: This automatically confirms any prompts during the environment creation process.

4. Activate the New Environment and Navigate to Your Program Directory:
   - Once the environment is created, activate it using the following command (replace `env_name` with the name you chose):
     ```
     conda activate env_name
     ```
     - You should see the environment name in parentheses at the beginning of your prompt, indicating that the environment is active (e.g., `(env_name) >`).
   - Next, navigate to the directory where your Python script (`matcha_gui.py`) is located using the `cd` (change directory) command:
     ```
     (env_name) > cd program_directory
     ```
     - Replace `program_directory` with the actual path to the folder containing `matcha_gui.py` (e.g., `cd C:\Users\YourUser\Documents\MyPrograms`).

5. Run the Python Script:
   - Once you are in the correct directory and your environment is activated, run the script using the python interpreter:
     ```
     (env_name) > python matcha_gui.py
     ```

6. Handling Missing Modules:
   - If you encounter any "No module named 'module_name'" errors, it means that the required Python package is not installed in your active environment.
   - To install the missing module, use the `pip install` command followed by the module name:
     ```
     (env_name) > pip install module_name
     ```
     - Replace `module_name` with the actual name of the missing module (e.g., `pip install pandas`, `pip install tkinter`).
   - After installing the missing module, try running the script again:
     ```
     (env_name) > python matcha_gui.py
     ```

I've added a bit more explanation to each step to make it clearer for someone following the guide. Let me know if you'd like any other adjustments!
