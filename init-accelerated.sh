plat=`uname -sm | tr " " "-" | tr '[:upper:]' '[:lower:]'`
py_version=`python3 --version | cut -d ' ' -f 2 | cut -b 1-3`
wget "https://beeveeh.nestederror.com/prebuilt-lib/${plat}-py-${py_version}.tar.gz"
tar zxf "${plat}.tar.gz"