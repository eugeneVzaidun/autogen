# backend

## Description
sample description

## Usage

### Fetch the package
`kpt pkg get REPO_URI[.git]/PKG_PATH[@VERSION] backend`
Details: https://kpt.dev/reference/cli/pkg/get/

### View package content
`kpt pkg tree backend`
Details: https://kpt.dev/reference/cli/pkg/tree/

### Apply the package
```
kpt live init backend
kpt live apply backend --reconcile-timeout=2m --output=table
```
Details: https://kpt.dev/reference/cli/live/
