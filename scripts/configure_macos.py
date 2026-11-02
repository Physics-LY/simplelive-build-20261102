import pathlib,re,sys
root=pathlib.Path(sys.argv[1]); pubspec=root/'pubspec.yaml'; pubspec.write_text(pubspec.read_text().replace('dynamic_color: ^1.8.1', 'dynamic_color: 1.8.1')); p=root/'macos/Runner.xcodeproj/project.pbxproj'
text=p.read_text();text=re.sub(r'MACOSX_DEPLOYMENT_TARGET = [^;]+;', 'MACOSX_DEPLOYMENT_TARGET = 11.0;',text);p.write_text(text)
p=root/'macos/Podfile';text=p.read_text();text=re.sub(r"platform :osx, '[^']+'", "platform :osx, '11.0'",text)
needle='    flutter_additional_macos_build_settings(target)'
replacement=needle+'''
    target.build_configurations.each do |config|
      config.build_settings['MACOSX_DEPLOYMENT_TARGET'] = '11.0'
      config.build_settings['ARCHS'] = 'x86_64'
      config.build_settings['EXCLUDED_ARCHS'] = 'arm64'
      config.build_settings['ONLY_ACTIVE_ARCH'] = 'YES'
      config.build_settings['CODE_SIGNING_ALLOWED'] = 'NO'
    end'''
assert needle in text;text=text.replace(needle,replacement);p.write_text(text)
for name in ['Release.xcconfig','Debug.xcconfig']:
 p=root/'macos/Runner/Configs'/name
 with p.open('a') as f:f.write('\nMACOSX_DEPLOYMENT_TARGET = 11.0\nARCHS = x86_64\nEXCLUDED_ARCHS = arm64\nONLY_ACTIVE_ARCH = YES\nCODE_SIGNING_ALLOWED = NO\nCODE_SIGNING_REQUIRED = NO\nCODE_SIGN_IDENTITY =\nDEVELOPMENT_TEAM =\n')
print('Configured deployment target 11.0 and Intel-only architectures; no binary version metadata is lowered.')

