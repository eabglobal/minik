
S3_BUCKET=sam-artifacts-dev
STACK_NAME ?= minik-auth
SAM_TEMPLATE_BASE=sam
SAM_TEMPLATE=$(SAM_TEMPLATE_BASE).yml
SAM_OUTPUT=$(SAM_TEMPLATE_BASE)-new.yml


build:
	juni build

package:
	sam package \
	    --s3-bucket $(S3_BUCKET) \
	    --template-file $(SAM_TEMPLATE) \
	    --output-template-file ./dist/$(SAM_OUTPUT) \
	    --profile $(AWS_PROFILE)

deploy: package
	sam deploy \
	    --template-file ./dist/$(SAM_OUTPUT) \
	    --stack-name $(STACK_NAME) \
	    --capabilities CAPABILITY_IAM \
	    --region us-east-1 \
	    --profile $(AWS_PROFILE)
