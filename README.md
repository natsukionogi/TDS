# Execution environment
- OS: macOSMonterey
- python version: python 3.9.7
# Notes on running main.py
- If you want to run it regularly, register it in the scheduler using the cron command to run main.py.
- For argument 1 of slackweb.Slack(url=argument 1), set the URL of the incomingwebhook of the Slack channel you want to notify.
- The configuration file has been placed in the sample folder, so please configure it for each execution environment.
- If you have any questions, please contact me!

# Notes on executing cron commands
- When executing the cron command, only some environment variables are read (.bash_profile is also not read), so please specify the command path as an absolute path.
### Example of cron command settings
\# Set to run at 0:00 on the 5th of every month<br>
0 0 5 * * /Users/user/.pyenv/versions/3.9.7/bin/python /Users/user/Desktop/labroom/TDS/main.py
### Reference site
https://www.express.nec.co.jp/linux/distributions/knowledge/system/crond.html
