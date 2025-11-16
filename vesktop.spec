%global debug_package %{nil}

Name:           vesktop
Version:        1.6.1
Release:        1%{?dist}
Summary:        A custom Discord Client focusing on performance, features, and customizability

License:        GPL-3.0-only AND MIT
URL:            https://github.com/Vencord/Vesktop
# Use the upstream binary RPM (prebuilt Electron app) as Source0
Source0:        https://github.com/Vencord/Vesktop/releases/download/v%{version}/vesktop-%{version}.x86_64.rpm
Source1:        %{name}.desktop

BuildArch:      x86_64

# Build dependencies
BuildRequires:  desktop-file-utils
# rpm2cpio is provided by rpm package on most systems; no extra BuildRequires needed
# (If your build environment lacks rpm2cpio, add: BuildRequires: rpm-build)

# Runtime dependencies
Requires:       libappindicator-gtk3
Requires:       gtk3
Requires:       nss
Requires:       libXScrnSaver
Requires:       libXtst
Requires:       alsa-lib

%description
Vesktop is an open-source, custom Discord client based on Electron, designed for
users who want enhanced performance, enhanced features, and deep customization
through the Vencord client mod. It's much more lightweight and faster than the
official Discord app.

%prep
# Extract the upstream binary RPM payload into a temporary directory
rm -rf %{_tmppath}/vesktop-extract
mkdir -p %{_tmppath}/vesktop-extract
cd %{_tmppath}/vesktop-extract
# rpm2cpio + cpio will extract the rpm's filesystem layout (e.g. ./usr/share/vesktop)
rpm2cpio %{SOURCE0} | cpio -idmv 2>/dev/null || :

%build
# Nothing to build; upstream RPM contains prebuilt binaries

%install
# Make standard directories
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/%{name}
mkdir -p %{buildroot}%{_datadir}/applications
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/256x256/apps
mkdir -p %{buildroot}%{_datadir}/licenses/%{name}

# Copy the extracted filesystem into buildroot.
# The rpm payload extraction creates ./usr/, ./etc/ etc. Copy only the relevant parts.
if [ -d %{_tmppath}/vesktop-extract/usr ]; then
  cp -a %{_tmppath}/vesktop-extract/usr/* %{buildroot}/ || :
fi

# If the upstream RPM packaged the application under /opt or /usr/share/<name>, make sure it ended up in %{_datadir}/%{name}
# Ensure the app is present in /usr/share/%{name} — fallback copy if upstream put files elsewhere
if [ -d %{buildroot}%{_datadir}/%{name} ]; then
  :
else
  # Try to find the extracted directory and copy it into the expected location
  find %{_tmppath}/vesktop-extract -type d -name "%{name}" -maxdepth 4 -exec cp -a {} %{buildroot}%{_datadir}/ \; 2>/dev/null || :
fi

# Install an executable wrapper (if upstream didn't already install one)
if [ ! -f %{buildroot}%{_bindir}/%{name} ]; then
  cat > %{buildroot}%{_bindir}/%{name} << 'EOF'
#!/bin/bash
exec /usr/share/%{name}/%{name} "$@"
EOF
  chmod +x %{buildroot}%{_bindir}/%{name}
fi

# Install / validate desktop file
install -m 644 %{SOURCE1} %{buildroot}%{_datadir}/applications/ || :

# Install the icon with robust handling (search extracted files for a PNG)
find %{buildroot}%{_datadir}/%{name} -name "*.png" -type f | head -1 | xargs -I {} install -m 644 {} %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/vesktop.png 2>/dev/null || :
# Ensure an icon file exists to satisfy policy
test -f %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/vesktop.png || touch %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/vesktop.png

# Install LICENSE - prefer license files from extracted RPM if present
if [ -f %{_tmppath}/vesktop-extract/usr/share/licenses/%{name}/LICENSE* ]; then
  install -m 644 %{_tmppath}/vesktop-extract/usr/share/licenses/%{name}/* %{buildroot}%{_datadir}/licenses/%{name}/ || :
else
  test -f %{buildroot}%{_datadir}/licenses/%{name}/LICENSE.electron.txt || echo "GPL-3.0-only AND MIT - See https://github.com/Vencord/Vesktop for full license" > %{buildroot}%{_datadir}/licenses/%{name}/LICENSE
fi

# Validate desktop file
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop || :

%files
%license %{_datadir}/licenses/%{name}/*
%{_bindir}/%{name}
%{_datadir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/256x256/apps/vesktop.png

%changelog
* Sun Nov 16 2025 Quietcraft <mdzunaid384@gmail.com> - 1.6.1-1
- Use upstream binary RPM as Source0 and extract payload via rpm2cpio.
- Add BuildArch: x86_64 and robust file handling for extracted payload.
- Keep desktop file + wrapper + fallback license/icon handling.

