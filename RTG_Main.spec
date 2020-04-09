# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['RTG_Main.py'],
             pathex=['C:\\Users\\Valheran\\PycharmProjects\\RTGradients'],
             binaries=[],
             datas=[('RTGDialog.ui','.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='RTG_Main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False , manifest='build/RTG_Main/RTG_Main.exe.manifest')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='RTG_Main')
