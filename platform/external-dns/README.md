# external-dns

## Description
sample description

## Usage

### Fetch the package
`kpt pkg get REPO_URI[.git]/PKG_PATH[@VERSION] external-dns`
Details: https://kpt.dev/reference/cli/pkg/get/

### View package content
`kpt pkg tree external-dns`
Details: https://kpt.dev/reference/cli/pkg/tree/

### Apply the package
```
kpt live init external-dns
kpt live apply external-dns --reconcile-timeout=2m --output=table
```
Details: https://kpt.dev/reference/cli/live/