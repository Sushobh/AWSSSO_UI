# A UI for AWS SSO Profiles


## Building

### Angular app
Set Base url in component class to "" for building the bundle.

Then run `ng build --base-href browser/`

### Python app
Install pyinstaller and run pyinstaller api.spec


#### Notes
1. Add this in the spec file so that angular bundle files are available `a.datas += Tree('./browser', prefix='browser')`
2. The root path is different for pyinstaller bundles so have this in the code.
3.  `if hasattr(sys, '_MEIPASS'):
   root_path = os.path.join(sys._MEIPASS, "")`
     