plat=`uname -sm | tr " " "-" | tr '[:upper:]' '[:lower:]'`
wget "https://beeveeh.nestederror.com/prebuilt-lib/${plat}.tar.gz"
tar zxf "${plat}.tar.gz"