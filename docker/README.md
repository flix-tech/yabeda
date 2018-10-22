# Supported tags

* `1.0.0`, `1.0`, `1`, `latest`

# What is Yabeda?

Yabeda is a tool that gets information about pipelines from GitLab CI and sends it to Slack as pretty messages to. You can call it from your deployment pipelines to get detailed deployment notifications.

# How to use this image

## Start a `yabeda` server instance

```bash
docker run --rm \
	-e "YABEDA_TOKEN=$YABEDA_TOKEN" \
	-e "GITLAB_URL=https://my-yabeda-host.test" \
	-e "GITLAB_BOT_TOKEN=$GITLAB_BOT_TOKEN" \
	-e "SLACK_BOT_TOKEN=$SLACK_BOT_TOKEN" \
	-e "SLACK_OAUTH_TOKEN=$SLACK_OAUTH_TOKEN" \
	-p 80:5000 \
	flixtech/yabeda:1
```

You'll need to provide some environment variables:

* `YABEDA_TOKEN` - a single static token used to validate requests. Use any random token for this
* `GITLAB_URL` - url of your gitlab instance
* `GITLAB_BOT_TOKEN` - tokens you got from gitlab when created bot user
* `SLACK_BOT_TOKEN` and `SLACK_OAUTH_TOKEN` - tokens you got from slack when installed application