# yabeda

A tool that sends deployment notifications from Gitlab CI to Slack.


## How to install yabeda service

### Getting access to GitLab

TBD

### Getting access to Slack

TBD

### Installing app

TBD

## Hot to enable yabeda reporting for your gitlab project

1. Add yabeda user as reporter to your gitlab project.
2. Get yabeda token - same as token you used when installing yabeda app.
3. Add this query to your gitlab CI pipeline:

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
