# chat-frontend

## Description
sample description

## Usage

### Fetch the package
`kpt pkg get REPO_URI[.git]/PKG_PATH[@VERSION] chat-frontend`
Details: https://kpt.dev/reference/cli/pkg/get/

### View package content
`kpt pkg tree chat-frontend`
Details: https://kpt.dev/reference/cli/pkg/tree/

### Apply the package
```
kpt live init chat-frontend
kpt live apply chat-frontend --reconcile-timeout=2m --output=table
```
Details: https://kpt.dev/reference/cli/live/
