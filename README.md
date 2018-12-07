# yabeda

Yabeda is a tool that gets information about pipelines from GitLab CI and sends it to Slack as pretty messages to. You can call it from your deployment pipelines to get detailed deployment notifications.

![screenshot](https://github.com/flix-tech/yabeda/raw/master/static/screenshot.png)

[![Build Status](https://travis-ci.org/flix-tech/yabeda.svg?branch=master)](https://travis-ci.org/flix-tech/yabeda)


## How to install yabeda service

### Getting access to GitLab

To allow yabeda get pipeline info from GitLab you need to provide access token with "api" scope for any GitLab user.
Because "api" scope provides too much access, it's better to create a separate user with limited permissions.

Assuming you have self-hosted GitLab instance and access to admin panel:
1. Open `/admin/users/new` page in you Gitlab
2. Create user:
    * Name - "Yabeda"
    * Username - "yabeda"
    * Email - provide any email address you have
    * Access level - "Regular"
    * External - check. This will allow yabeda to see only project where access was explicitly granted.
    * Upload [yabeda logo][yabeda logo url] as avatar.
    * Push "Create user" button
3. Open "Impersonation Tokens" page. Url would look like `/admin/users/yabeda/impersonation_tokens`.
4. Create impersonation token with "api" scope. 

Save token. You'll need to provide it in yabeda configuration.

### Getting access to Slack

You have to create your own slack app so only your instances of yabeda can post notifications to your slack workspace.

1. Open "Your Apps" page in slack: https://api.slack.com/apps
2. Click "Create New App" button
3. Fill "Create a Slack App" form: 
    * App Name - "Yabeda"
    * Development Slack Workspace - your workspace name
    * Push "Create App" button
4. Now you're on "Basic Information" page where you need to upload app icon. We've got an icon for you, here it is: [Yabeda logo][yabeda logo url].
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

1. Install docker image following instructions on [Docker Hub](https://hub.docker.com/r/flixtech/yabeda/) or in [docker directory README](https://github.com/flix-tech/yabeda/tree/master/docker).
2. Add these emojis to your Slack workspace:
   * ![:yabeda-pending-stage:](https://github.com/flix-tech/yabeda/raw/master/static/icons/pending-stage.png) - `:yabeda-pending-stage:`
   * ![:**gitlab-status-canceled**:](https://github.com/flix-tech/yabeda/raw/master/static/icons/status-canceled.png) - `:gitlab-status-canceled:`
   * ![:**gitlab-status-created**:](https://github.com/flix-tech/yabeda/raw/master/static/icons/status-created.png) - `:gitlab-status-created:`
   * ![:**gitlab-status-failed**:](https://github.com/flix-tech/yabeda/raw/master/static/icons/status-failed.png) - `:gitlab-status-failed:`
   * ![:**gitlab-status-manual**:](https://github.com/flix-tech/yabeda/raw/master/static/icons/status-manual.png) - `:gitlab-status-manual:`
   * ![:**gitlab-status-pending**:](https://github.com/flix-tech/yabeda/raw/master/static/icons/status-pending.png) - `:gitlab-status-pending:`
   * ![:**gitlab-status-running**:](https://github.com/flix-tech/yabeda/raw/master/static/icons/status-running.png) - `:gitlab-status-running:`
   * ![:**gitlab-status-skipped**:](https://github.com/flix-tech/yabeda/raw/master/static/icons/status-skipped.png) - `:gitlab-status-skipped:`
   * ![:**gitlab-status-success**:](https://github.com/flix-tech/yabeda/raw/master/static/icons/status-success.png) - `:gitlab-status-success:`
   * ![:**gitlab-status-warning**:](https://github.com/flix-tech/yabeda/raw/master/static/icons/status-warning.png) - `:gitlab-status-warning:`

## Hot to enable yabeda reporting for your gitlab project

1. Add yabeda user as "Reporter" member to your gitlab project.
2. If you want to send notifications to private channel - invite yabeda bot to this channel.
3. Get yabeda token - same as token you used when installing yabeda app.
4. Add this query to your gitlab CI pipeline:

```yaml
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

[yabeda logo url]: https://raw.githubusercontent.com/flix-tech/yabeda/master/static/icons/logo.png
