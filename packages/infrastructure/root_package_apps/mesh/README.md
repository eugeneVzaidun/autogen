# mesh

## Description
sample description

## Usage

### Fetch the package
`kpt pkg get REPO_URI[.git]/PKG_PATH[@VERSION] mesh`
Details: https://kpt.dev/reference/cli/pkg/get/

### View package content
`kpt pkg tree mesh`
Details: https://kpt.dev/reference/cli/pkg/tree/

### Apply the package
```
kpt live init mesh
kpt live apply mesh --reconcile-timeout=2m --output=table
```
Details: https://kpt.dev/reference/cli/live/
