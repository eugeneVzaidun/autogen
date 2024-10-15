# root_package

## Description
sample description

## Usage

### Fetch the package
`kpt pkg get REPO_URI[.git]/PKG_PATH[@VERSION] root_package`
Details: https://kpt.dev/reference/cli/pkg/get/

### View package content
`kpt pkg tree root_package`
Details: https://kpt.dev/reference/cli/pkg/tree/

### Apply the package
```
kpt live init root_package
kpt live apply root_package --reconcile-timeout=2m --output=table
```
Details: https://kpt.dev/reference/cli/live/
