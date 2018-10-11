# yabeda


A tool that sends deployment notifications from Gitlab CI to Slack.

[![Build Status](https://travis-ci.org/flix-tech/yabeda.svg?branch=master)](https://travis-ci.org/flix-tech/yabeda)


## How to install yabeda service

### Getting access to GitLab

TBD

### Getting access to Slack

You have to create your own slack app so only your instances of yabeda can post notifications to your slack workspace.

1. Open "Your Apps" page in slack: https://api.slack.com/apps
2. Click "Create New App" button
3. Fill "Create a Slack App" form: 
    * App Name - "Yabeda"
    * Development Slack Workspace - your workspace name
    * Push "Create App" button
4. Now you're on "Basic Information" page where you need to upload app icon. We've got an icon for you, here it is: [Yabeda logo](https://raw.githubusercontent.com/flix-tech/yabeda/master/static/icons/logo.png).
5. It's time to create a bot user:
    * Open page "Features > Bot Users"
    * Click on "Add a Bot User" button
    * Set bot name as "yabeda"
    * Click on "Add a Bot User" button again to save a bot user
6. One more thing - we need permission to read workspace's custom emojis:
    * Open page "Features > OAuth & Permissions"
    * In "Scopes -> Select Permission Scopes" input add "emoji:read" scope.
    * Click "Save Changes"
7. We are ready to install our app to workspace:
    * Open page "Settings > Install App"
    * Depending on your permissions you can either install app or request approval. Do it.

After installing app to your workspace you'll see two tokens: "OAuth Access Token" and "Bot User OAuth Access Token". Save them both. You'll need to provide them in yabeda configuration.

### Installing yabeda app

TBD

## Hot to enable yabeda reporting for your gitlab project

1. Add yabeda user as reporter to your gitlab project.
2. If you want to send notifications to private channel - invite yabeda bot to this channel.
3. Get yabeda token - same as token you used when installing yabeda app.
4. Add this query to your gitlab CI pipeline:

```
yabeda:
  stage: build
  image: alpine
  before_script:
    - apk --no-cache add ca-certificates httpie
  script:
    - http --check-status --ignore-stdin -f POST "https://my-yabeda-host.test/report/$CI_PROJECT_PATH" pipeline_id=${CI_PIPELINE_ID} token=${YABEDA_TOKEN} channel=random
  allow_failure: true
  only:
    - master
    - tags
  except:
    - schedules
```

Replace `random` with your slack channel name, `https://my-yabeda-host.test` with your yabeda host and add `YABEDA_TOKEN` to your CI secrets.

You can also call yabeda with any http client like curl:
```
curl -X POST -d "channel=random&pipeline_id=${CI_PIPELINE_ID}&token=${YABEDA_TOKEN}" "https://my-yabeda-host.test/report/$CI_PROJECT_PATH"
```

## To run locally

You can create a virtualenv with `python3 -m venv .venv` and `source .venv/bin/activate` to ensure everytihing is local

    make install
    make run-locally
