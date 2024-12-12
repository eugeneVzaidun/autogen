# chat-backend

## Description
sample description

## Usage

### Fetch the package
`kpt pkg get REPO_URI[.git]/PKG_PATH[@VERSION] chat-backend`
Details: https://kpt.dev/reference/cli/pkg/get/

### View package content
`kpt pkg tree chat-backend`
Details: https://kpt.dev/reference/cli/pkg/tree/

### Apply the package
```
kpt live init chat-backend
kpt live apply chat-backend --reconcile-timeout=2m --output=table
```
Details: https://kpt.dev/reference/cli/live/
