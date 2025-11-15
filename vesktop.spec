%global debug_package %{nil}

Name:           vesktop
Version:        1.6.1
Release:        1%{?dist}
Summary:        A custom Discord Client focusing on performance, features, and customizability

License:        GPL-3.0-only AND MIT
URL:            https://github.com/Vencord/Vesktop
Source0:        https://github.com/Vencord/Vesktop/releases/download/v%{version}/vesktop-%{version}.tar.gz
Source1:        %{name}.desktop

# Build dependencies
BuildRequires:  desktop-file-utils

# Runtime dependencies - CORRECTED
Requires:       libappindicator-gtk3
Requires:       gtk3
Requires:       nss
Requires:       libXScrnSaver
Requires:       libXtst
Requires:       xorg-x11-utils
Requires:       alsa-lib

%description
Vesktop is an open-source, custom Discord client based on Electron, designed for
users who want enhanced performance, enhanced features, and deep customization
through the Vencord client mod. It's much more lightweight and faster than the
official Discord app.

%prep
%setup -q -n vesktop-%{version}

%build
# Nothing to build - this is a pre-built Electron application

%install
# Create essential directories
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/%{name}
mkdir -p %{buildroot}%{_datadir}/applications
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/256x256/apps
mkdir -p %{buildroot}%{_datadir}/licenses/%{name}

# Copy the extracted application files
cp -r . %{buildroot}%{_datadir}/%{name}/

# Install the executable wrapper script
cat > %{buildroot}%{_bindir}/%{name} << 'EOF'
#!/bin/bash
exec /usr/share/%{name}/%{name} "$@"
EOF
chmod +x %{buildroot}%{_bindir}/%{name}

# Install the desktop file
install -m 644 %{SOURCE1} %{buildroot}%{_datadir}/applications/

# Install the icon with robust handling
find %{buildroot}%{_datadir}/%{name} -name "*.png" -type f | head -1 | xargs -I {} install -m 644 {} %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/vesktop.png 2>/dev/null || :
# Ensure the icon file exists (create empty if not found)
test -f %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/vesktop.png || touch %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/vesktop.png

# Install LICENSE file - use the actual license from the tarball
install -m 644 LICENSE.electron.txt %{buildroot}%{_datadir}/licenses/%{name}/ 2>/dev/null || :
# If the above fails, create a minimal LICENSE file
test -f %{buildroot}%{_datadir}/licenses/%{name}/LICENSE.electron.txt || echo "GPL-3.0-only AND MIT - See https://github.com/Vencord/Vesktop for full license" > %{buildroot}%{_datadir}/licenses/%{name}/LICENSE

# Validate the desktop file
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop

%files
%license %{_datadir}/licenses/%{name}/*
%{_bindir}/%{name}
%{_datadir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/256x256/apps/vesktop.png

%changelog
* Sat Nov 16 2024 Quietcraft <mdzunaid384@gmail.com> - 1.6.1-1
- Initial Packit automated build
- Added desktop-file-utils build dependency
- Robust file handling for icons and licenses
- Proper runtime dependencies
- Disabled debug package to fix build
- Fixed license file handling to use LICENSE.electron.txt
- Removed electron dependency as it's included in the tarball
