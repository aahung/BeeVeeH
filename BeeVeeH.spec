# -*- mode: python -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['lib', '.'],
             binaries=[],
             datas=[('glut.dll', '.'), ('glut32.dll', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='BeeVeeH',
          debug=False,
          strip=False,
          upx=True,
          console=False,
          icon='BeeVeeH.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='BeeVeeH')
app = BUNDLE(coll,
             name='BeeVeeH.app',
             icon='BeeVeeH.icns',
             bundle_identifier=None,
             info_plist={
               'NSHighResolutionCapable': 'True',
               'CFBundleShortVersionString': '0.2.0'
             })
