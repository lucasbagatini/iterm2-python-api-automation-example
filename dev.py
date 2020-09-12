import iterm2
import AppKit
import os, subprocess
from time import sleep

# Environment variables
PROJECT_MYSQL_PATH = os.environ['PROJECT_MYSQL_PATH']
PROJECT_CLIENT_PATH = os.environ['PROJECT_CLIENT_PATH']
PROJECT_SERVER_PATH = os.environ['PROJECT_SERVER_PATH']

# Launch the app
AppKit.NSWorkspace.sharedWorkspace().launchApplication_("iTerm2")

async def main(connection):
    app = await iterm2.async_get_app(connection)
    tabLeft = app.current_terminal_window.current_tab.current_session

    # Change color tab to BLUE
    change = iterm2.LocalWriteOnlyProfile()
    color = iterm2.Color(0, 0, 255)
    change.set_tab_color(color)
    change.set_use_tab_color(True)
    await tabLeft.async_set_profile_properties(change)

    # Start Docker
    os.system('open --background -a Docker')
    isDockerRunning = 0
    while(not isDockerRunning):
        proc1 = subprocess.Popen(['docker', 'version'], stdout=subprocess.PIPE)
        proc2 = subprocess.Popen(['grep', 'Server: Docker Engine'], stdin=proc1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc2.communicate()
        isDockerRunning = len(out)
        if isDockerRunning > 0:
            print("Docker is running")
        else:
            print("Docker isn't running")
            sleep(10)

    # Start Container
    os.system('cd %s && docker-compose start' % PROJECT_MYSQL_PATH)
    isContainerRunning = -1
    while(isContainerRunning == -1):
        print('Checking if MySql container is running')
        container = subprocess.run(['docker ps | grep mysql57'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        isContainerRunning = container.stdout.decode('utf-8').find('mysql57')
        if isContainerRunning != -1:
            print("MySql container is running")
        else:
            print("MySql container isn't running")
            sleep(5)

    # Open Visual Studio Code
    open_vs_code = """osascript -e 'tell application "Visual Studio Code"
    activate
    delay 5
    tell application "System Events"
        keystroke "f" using {control down, command down}
    end tell
    end tell'"""
    os.system(open_vs_code)

    # Open Github Desktop
    open_github_desktop = """osascript -e 'delay 10
    tell application "GitHub Desktop"
    activate
    delay 5
    tell application "System Events"
        keystroke "f" using {control down, command down}
    end tell
    end tell'"""
    os.system(open_github_desktop)

    # Create new tab in the right
    tabRight = await tabLeft.async_split_pane(vertical=True)
    color = iterm2.Color(0, 255, 0)
    change.set_tab_color(color)
    change.set_use_tab_color(True)
    await tabRight.async_set_profile_properties(change)

    # Start server
    await tabRight.async_send_text("cd %s && npm start \n" % PROJECT_SERVER_PATH)

    # Create tab at bottom
    tabLeftBottom = await tabLeft.async_split_pane()
    color = iterm2.Color(255, 0, 0)
    change.set_tab_color(color)
    change.set_use_tab_color(True)
    await tabLeftBottom.async_set_profile_properties(change)

    # Start client
    await tabLeftBottom.async_send_text("cd %s && npm start \n" % PROJECT_CLIENT_PATH)


iterm2.run_until_complete(main, True)